"""Thin client for the Google Photos Picker API.

Since March 2025 the Library API can only read media created by the calling app, so the
Picker API is the only official way to read a user's existing photos: the user selects
items in the Google Photos UI and the app then lists the picked items.
"""

import time
from collections.abc import Callable, Iterator

import httpx
from loguru import logger

from seenery.photos.models import PickedMediaItem, PickingSession, parse_duration

PICKER_API_URL = "https://photospicker.googleapis.com/v1/"


class PickerTimeoutError(TimeoutError):
    """The user did not finish picking before the session timed out."""


class PickerClient:
    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    @classmethod
    def from_token(cls, token: str, *, timeout: float) -> PickerClient:
        http = httpx.Client(
            base_url=PICKER_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )
        return cls(http)

    def close(self) -> None:
        self._http.close()

    def create_session(self) -> PickingSession:
        response = self._http.post("sessions", json={})
        response.raise_for_status()
        return PickingSession.model_validate(response.json())

    def get_session(self, session_id: str) -> PickingSession:
        response = self._http.get(f"sessions/{session_id}")
        response.raise_for_status()
        return PickingSession.model_validate(response.json())

    def delete_session(self, session_id: str) -> None:
        response = self._http.delete(f"sessions/{session_id}")
        response.raise_for_status()

    def wait_until_picked(
        self,
        session: PickingSession,
        *,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> PickingSession:
        """Poll the session, as advised by its polling config, until the user is done picking."""
        interval = parse_duration(session.polling_config.poll_interval)
        deadline = clock() + parse_duration(session.polling_config.timeout_in)
        while not session.media_items_set:
            if clock() >= deadline:
                raise PickerTimeoutError(f"Picking session {session.id} timed out")
            sleep(interval)
            session = self.get_session(session.id)
            logger.debug("Session {} media_items_set={}", session.id, session.media_items_set)
        return session

    def list_media_items(self, session_id: str, page_size: int = 100) -> Iterator[PickedMediaItem]:
        params: dict[str, str | int] = {"sessionId": session_id, "pageSize": page_size}
        while True:
            response = self._http.get("mediaItems", params=params)
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("mediaItems", []):
                yield PickedMediaItem.model_validate(item)
            page_token = payload.get("nextPageToken")
            if not page_token:
                return
            params["pageToken"] = page_token
