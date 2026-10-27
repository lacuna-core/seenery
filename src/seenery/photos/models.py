"""Pydantic models for the Google Photos Picker API responses.

See https://developers.google.com/photos/picker/reference/rest
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, frozen=True)


class PollingConfig(_ApiModel):
    poll_interval: str = "5s"
    timeout_in: str = "1800s"


class PickingSession(_ApiModel):
    id: str
    picker_uri: str
    media_items_set: bool = False
    polling_config: PollingConfig = PollingConfig()


class MediaFile(_ApiModel):
    base_url: str
    mime_type: str
    filename: str = ""


class PickedMediaItem(_ApiModel):
    id: str
    create_time: datetime
    type: str = "TYPE_UNSPECIFIED"
    media_file: MediaFile | None = None


def parse_duration(value: str) -> float:
    """Parse a protobuf JSON duration such as ``"5s"`` or ``"1.5s"`` into seconds."""
    return float(value.removesuffix("s"))
