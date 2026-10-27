"""OAuth 2.0 (installed-app flow) for the Google Photos Picker API."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from loguru import logger

PICKER_SCOPES = ["https://www.googleapis.com/auth/photospicker.mediaitems.readonly"]


def load_access_token(
    client_secrets_file: Path, token_file: Path, *, open_browser: bool = True
) -> str:
    """Return a valid access token, reusing/refreshing the cached one or running the OAuth flow."""
    creds: Credentials | None = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
            str(token_file), PICKER_SCOPES
        )

    if creds is not None and creds.valid:
        return str(creds.token)

    if creds is not None and creds.expired and creds.refresh_token:
        logger.debug("Refreshing cached Google token")
        creds.refresh(Request())  # type: ignore[no-untyped-call]
    else:
        if not client_secrets_file.exists():
            raise FileNotFoundError(
                f"OAuth client secrets not found at {client_secrets_file}. "
                "Download a 'Desktop app' OAuth client JSON from Google Cloud Console."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), PICKER_SCOPES)
        creds = flow.run_local_server(port=0, open_browser=open_browser)

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json())
    token_file.chmod(0o600)
    return str(creds.token)
