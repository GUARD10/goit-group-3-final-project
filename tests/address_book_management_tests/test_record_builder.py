from datetime import date, datetime

import pytest

from bll.entity_builders.record_builder.record_builder import RecordBuilder
from dal.entities.phone import Phone
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError


@pytest.fixture
def base_record():
    return Record("Roman", "+380931112233")


@pytest.fixture
def builder(base_record):
    return RecordBuilder(base_record)


def test_set_name_success(builder):
    builder.set_name("New Name")
    assert builder._record.name.value == "New Name"


@pytest.mark.parametrize("bad_name", ["", "   ", None])
def test_set_name_invalid(builder, bad_name):
    with pytest.raises(InvalidError, match="Name cannot be empty"):
        builder.set_name(bad_name)


def test_build_returns_record(builder):
    record = builder.build()
    assert isinstance(record, Record)


def test_build_raises_if_name_invalid(base_record):
    base_record.name.value = " "
    builder = RecordBuilder(base_record)
    with pytest.raises(InvalidError):
        builder.build()


def test_add_phone_success(builder):
    builder.add_phone("+380987654321")
    assert any(p.value == "+380987654321" for p in builder._record.phones)


def test_add_phone_object(builder):
    phone = Phone("+380555555555")
    builder.add_phone(phone)
    assert any(p.value == "+380555555555" for p in builder._record.phones)


def test_add_phone_duplicate_raises(builder):
    with pytest.raises(AlreadyExistsError):
        builder.add_phone(builder._record.phones[0].value)


def test_update_phone_success(builder):
    old = builder._record.phones[0].value
    builder.remove_phone(old)
    builder.add_phone("+380111111111")
    assert any(p.value == "+380111111111" for p in builder._record.phones)


def test_update_phone_not_found_raises(builder):
    with pytest.raises(NotFoundError):
        builder.remove_phone("999999")


def test_remove_phone_success(builder):
    phone = builder._record.phones[0].value
    builder.remove_phone(phone)
    assert all(p.value != phone for p in builder._record.phones)


def test_remove_phone_not_found(builder):
    with pytest.raises(NotFoundError):
        builder.remove_phone("nope")


def test_clear_phones(builder):
    builder.add_phone("+380111111111")
    builder.add_phone("+380222222222")
    builder.clear_phones()
    assert builder._record.phones == []


def test_set_birthday_from_str(builder):
    builder.set_birthday("2000-05-20")
    assert builder._record.birthday.value == date(2000, 5, 20)


def test_set_birthday_from_date(builder):
    d = date(1999, 1, 1)
    builder.set_birthday(d)
    assert builder._record.birthday.value == d


def test_set_birthday_from_datetime(builder):
    dt = datetime(2005, 7, 15, 14, 0)
    builder.set_birthday(dt)
    assert builder._record.birthday.value == date(2005, 7, 15)


def test_clear_birthday(builder):
    builder.set_birthday("1990-01-01")
    builder.clear_birthday()
    assert builder._record.birthday is None
