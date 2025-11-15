from datetime import date, datetime

from bll.helpers.CalendarRenderer import render_calendar_with_clock
from dal.entities.Record import Record


def test_render_calendar_includes_birthdays_and_time_without_summary():
    records = [
        Record("Alice", birthday=date(1990, 5, 5)),
        Record("Bob", birthday=date(1985, 5, 12)),
    ]
    now = datetime(2024, 5, 4, 10, 30, 0)

    result = render_calendar_with_clock(records, month=5, year=2024, now=now)

    assert "Alice" in result
    assert "Bob" in result
    assert "May 2024" in result
    assert "Current Time" in result
    assert "Saturday" in result  # from the timestamp header
    assert "Birthdays in" not in result  # summary table removed


def test_render_calendar_adjusts_leap_birthdays():
    records = [Record("Leap", birthday=date(2000, 2, 29))]
    now = datetime(2025, 2, 1, 9, 0, 0)

    result = render_calendar_with_clock(records, month=2, year=2025, now=now)

    assert "Leap" in result
    assert "28" in result  # leap birthdays are shifted in non-leap years


def test_render_calendar_defaults_to_current_month():
    records = [Record("Carol", birthday=date(1992, 8, 14))]
    now = datetime(2024, 8, 10, 8, 0, 0)

    result = render_calendar_with_clock(records, now=now)

    assert "August 2024" in result
    assert "January 2024" not in result
    assert "December 2024" not in result
    assert "Carol" in result
