"""Daily summary of picked photos."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, tzinfo

from seenery.photos.models import PickedMediaItem


@dataclass(frozen=True)
class DailySummary:
    day: date
    photo_count: int
    first_photo: PickedMediaItem


def build_daily_report(
    items: Iterable[PickedMediaItem], *, since: datetime, tz: tzinfo | None = None
) -> list[DailySummary]:
    """Group photos created at or after ``since`` by day in ``tz`` (default: local), oldest first."""
    by_day: dict[date, list[PickedMediaItem]] = {}
    for item in items:
        if item.type != "PHOTO" or item.create_time < since:
            continue
        by_day.setdefault(item.create_time.astimezone(tz).date(), []).append(item)

    return [
        DailySummary(
            day=day,
            photo_count=len(photos),
            first_photo=min(photos, key=lambda p: p.create_time),
        )
        for day, photos in sorted(by_day.items())
    ]
