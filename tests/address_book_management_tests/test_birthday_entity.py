from datetime import date, datetime, timedelta

import pytest

from dal.entities.birthday import Birthday
from dal.exceptions.invalid_error import InvalidError


def test_valid_birthday_from_string():
    b = Birthday("05.11.2000")
    assert b.value == date(2000, 11, 5)


def test_valid_birthday_from_date():
    d = date(1999, 12, 31)
    b = Birthday(d)
    assert b.value == d


def test_valid_birthday_from_datetime():
    dt = datetime(1990, 5, 10, 15, 30)
    b = Birthday(dt)
    assert b.value == date(1990, 5, 10)


def test_future_birthday_raises():
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(InvalidError, match="Birthday cannot be in the future"):
        Birthday(future_date)


def test_invalid_string_format_raises():
    with pytest.raises(InvalidError, match="Birthday must be in format"):
        Birthday("2000/11/05")


def test_invalid_type_raises():
    with pytest.raises(InvalidError, match="Birthday value must be"):
        Birthday(12345)









