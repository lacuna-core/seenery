from datetime import UTC, date, datetime

from seenery.photos.models import PickedMediaItem
from seenery.photos.report import build_daily_report


def _item(item_id: str, created: str, kind: str = "PHOTO") -> PickedMediaItem:
    return PickedMediaItem.model_validate({"id": item_id, "createTime": created, "type": kind})


def test_groups_by_day_and_picks_earliest_photo() -> None:
    items = [
        _item("b", "2026-10-02T15:00:00Z"),
        _item("a", "2026-10-02T08:00:00Z"),
        _item("c", "2026-10-01T12:00:00Z"),
        _item("video", "2026-10-01T07:00:00Z", kind="VIDEO"),
        _item("old", "2026-09-01T12:00:00Z"),
    ]

    report = build_daily_report(items, since=datetime(2026, 9, 27, tzinfo=UTC), tz=UTC)

    assert [(s.day, s.photo_count, s.first_photo.id) for s in report] == [
        (date(2026, 10, 1), 1, "c"),
        (date(2026, 10, 2), 2, "a"),
    ]


def test_empty_input() -> None:
    assert build_daily_report([], since=datetime(2026, 1, 1, tzinfo=UTC)) == []
