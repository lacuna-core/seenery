from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from seenery.cli.app import app
from seenery.photos import auth, picker
from seenery.photos.models import PickedMediaItem, PickingSession

runner = CliRunner()


class _FakePicker:
    def __init__(self, items: list[PickedMediaItem]) -> None:
        self._items = items
        self.deleted: list[str] = []

    def create_session(self) -> PickingSession:
        return PickingSession(id="s1", picker_uri="https://picker/s1")

    def wait_until_picked(self, session: PickingSession) -> PickingSession:
        return session

    def list_media_items(self, session_id: str) -> Iterator[PickedMediaItem]:
        yield from self._items

    def delete_session(self, session_id: str) -> None:
        self.deleted.append(session_id)

    def close(self) -> None:
        pass


def _install_fakes(monkeypatch: pytest.MonkeyPatch, items: list[PickedMediaItem]) -> _FakePicker:
    fake = _FakePicker(items)
    monkeypatch.setattr(auth, "load_access_token", lambda *a, **k: "token")
    monkeypatch.setattr(picker.PickerClient, "from_token", lambda *a, **k: fake)
    return fake


def test_photos_report(monkeypatch: pytest.MonkeyPatch) -> None:
    created = datetime.now(UTC) - timedelta(days=1)
    item = PickedMediaItem.model_validate(
        {
            "id": "1",
            "createTime": created.isoformat(),
            "type": "PHOTO",
            "mediaFile": {"baseUrl": "u", "mimeType": "image/jpeg", "filename": "IMG_1.jpg"},
        }
    )
    fake = _install_fakes(monkeypatch, [item, item])

    result = runner.invoke(app, ["photos", "--no-open-browser"])

    assert result.exit_code == 0, result.output
    assert created.astimezone().date().isoformat() in result.output
    assert "Number of photos: 2" in result.output
    assert "IMG_1.jpg" in result.output
    assert fake.deleted == ["s1"]


def test_photos_no_matches(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fakes(monkeypatch, [])

    result = runner.invoke(app, ["photos", "--no-open-browser", "--days", "7"])

    assert result.exit_code == 0
    assert "No photos from the last 7 days" in result.output


def test_photos_missing_secrets(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _raise(*_: Any, **__: Any) -> str:
        raise FileNotFoundError("OAuth client secrets not found")

    monkeypatch.setattr(auth, "load_access_token", _raise)

    result = runner.invoke(app, ["photos", "--no-open-browser"])

    assert result.exit_code == 1
    assert "client secrets not found" in result.output
