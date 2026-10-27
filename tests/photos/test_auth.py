import json
from pathlib import Path
from typing import Any

import pytest

from seenery.photos import auth


class _FakeCreds:
    token = "fresh-token"

    def to_json(self) -> str:
        return json.dumps({"token": self.token})


class _FakeFlow:
    def run_local_server(self, **_: Any) -> _FakeCreds:
        return _FakeCreds()


def test_missing_client_secrets(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        auth.load_access_token(tmp_path / "missing.json", tmp_path / "token.json")


def test_runs_flow_and_caches_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secrets = tmp_path / "client_secret.json"
    secrets.write_text("{}")
    token_file = tmp_path / "cache" / "token.json"
    monkeypatch.setattr(
        "google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file",
        lambda *a, **k: _FakeFlow(),
    )

    assert auth.load_access_token(secrets, token_file, open_browser=False) == "fresh-token"
    assert json.loads(token_file.read_text()) == {"token": "fresh-token"}
    assert token_file.stat().st_mode & 0o777 == 0o600
