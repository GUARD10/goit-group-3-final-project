import pytest
from datetime import date, datetime, timedelta
from bll.helpers.DateHelper import DateHelper
from dal.exceptions.InvalidException import InvalidException

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
    with pytest.raises(InvalidException):
        DateHelper.parse_to_date("31-10-2024")

def test_parse_none_value():
    with pytest.raises(InvalidException):
        DateHelper.parse_to_date(None)
