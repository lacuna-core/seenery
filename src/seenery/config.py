from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LACUNA_", env_file=".env", extra="ignore", frozen=True
    )

    request_timeout: float = 30.0
    log_level: str = "INFO"

    google_client_secrets_file: Path = Path("client_secret.json")
    google_token_file: Path = Path.home() / ".config" / "seenery" / "google_token.json"


SETTINGS = Settings()
