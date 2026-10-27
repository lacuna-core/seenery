import json

import httpx
import pytest

from seenery.photos.models import PickingSession, parse_duration
from seenery.photos.picker import PICKER_API_URL, PickerClient, PickerTimeoutError

SESSION = {
    "id": "s1",
    "pickerUri": "https://photos.google.com/picker/s1",
    "pollingConfig": {"pollInterval": "2s", "timeoutIn": "10s"},
    "mediaItemsSet": False,
}


def _client(handler: httpx.MockTransport) -> PickerClient:
    return PickerClient(httpx.Client(base_url=PICKER_API_URL, transport=handler))


def test_parse_duration() -> None:
    assert parse_duration("5s") == 5.0
    assert parse_duration("1.5s") == 1.5


def test_create_and_delete_session() -> None:
    calls: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(200, json=SESSION)
        return httpx.Response(200, json={})

    client = _client(httpx.MockTransport(handler))
    session = client.create_session()
    client.delete_session(session.id)

    assert session.picker_uri == SESSION["pickerUri"]
    assert calls == [("POST", "/v1/sessions"), ("DELETE", "/v1/sessions/s1")]


def test_wait_until_picked_polls_until_set() -> None:
    responses = iter([SESSION, {**SESSION, "mediaItemsSet": True}])
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=next(responses))

    client = _client(httpx.MockTransport(handler))
    result = client.wait_until_picked(
        PickingSession.model_validate(SESSION), sleep=sleeps.append, clock=lambda: 0.0
    )

    assert result.media_items_set
    assert sleeps == [2.0, 2.0]


def test_wait_until_picked_times_out() -> None:
    now = iter([0.0, 11.0])
    client = _client(httpx.MockTransport(lambda r: httpx.Response(500)))

    with pytest.raises(PickerTimeoutError):
        client.wait_until_picked(
            PickingSession.model_validate(SESSION), sleep=lambda _: None, clock=lambda: next(now)
        )


def test_list_media_items_follows_pagination() -> None:
    pages = {
        None: {
            "mediaItems": [{"id": "1", "createTime": "2026-10-01T00:00:00Z", "type": "PHOTO"}],
            "nextPageToken": "p2",
        },
        "p2": {"mediaItems": [{"id": "2", "createTime": "2026-10-02T00:00:00Z"}]},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["sessionId"] == "s1"
        return httpx.Response(200, content=json.dumps(pages[request.url.params.get("pageToken")]))

    items = list(_client(httpx.MockTransport(handler)).list_media_items("s1"))

    assert [i.id for i in items] == ["1", "2"]
    assert items[1].type == "TYPE_UNSPECIFIED"
