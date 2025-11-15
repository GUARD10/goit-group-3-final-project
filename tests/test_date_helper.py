from datetime import date, timedelta

import pytest

from bll.helpers.date_helper import DateHelper
from dal.exceptions.invalid_error import InvalidError


def test_date_within_next_week():
    today = date.today()
    in_three_days = today + timedelta(days=3)
    assert DateHelper.is_date_within_next_week(in_three_days, today)


def test_date_after_week():
    today = date.today()
    in_ten_days = today + timedelta(days=10)
    assert not DateHelper.is_date_within_next_week(in_ten_days, today)


def test_leap_year_feb_edge_case():
    leap = date(2020, 2, 29)
    adjusted = DateHelper.set_date_with_feb_edge_case(leap, 2021)
    assert adjusted == date(2021, 2, 28)


def test_parse_valid_formats():
    assert DateHelper.parse_to_date("2024-10-31")
    assert DateHelper.parse_to_date("31.10.2024")
    assert DateHelper.parse_to_date("2024.10.31")
    assert DateHelper.parse_to_date("31/10/2024")


def test_parse_invalid_format():
    with pytest.raises(InvalidError):
        DateHelper.parse_to_date("31-10-2024")


def test_parse_none_value():
    with pytest.raises(InvalidError):
        DateHelper.parse_to_date(None)


def test_cross_year_window_includes_next_year_birthday():
    # today: Dec 31, event: Jan 1 (any past year) should be within next 2 days
    dec31 = date(2024, 12, 31)
    jan1_any = date(2000, 1, 1)
    assert DateHelper.is_date_within_next_week(jan1_any, dec31, days=2)

    # window = 1 day (Dec 31 to Jan 1 inclusive) should include
    assert DateHelper.is_date_within_next_week(jan1_any, dec31, days=1)









