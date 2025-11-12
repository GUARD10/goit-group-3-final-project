import pytest
from datetime import date, datetime

from dal.entities.Record import Record
from dal.entities.Phone import Phone
from dal.entities.Birthday import Birthday
from dal.Exceptions.InvalidException import InvalidException
from dal.Exceptions.AlreadyExistException import AlreadyExistException
from dal.Exceptions.NotFoundException import NotFoundException
from dal.entity_builders.RecordBuilder.RecordBuilder import RecordBuilder


@pytest.fixture
def base_record():
    """Базовий контакт для більшості тестів."""
    return Record("Roman", "+380931112233")


@pytest.fixture
def builder(base_record):
    """Повертає RecordBuilder з базовим записом."""
    return RecordBuilder(base_record)


# --- SET NAME --- #

def test_set_name_success(builder):
    builder.set_name("New Name")
    assert builder._record.name.value == "New Name"


@pytest.mark.parametrize("bad_name", ["", "   ", None])
def test_set_name_invalid(builder, bad_name):
    with pytest.raises(InvalidException, match="Name cannot be empty"):
        builder.set_name(bad_name)


# --- BUILD --- #

def test_build_returns_record(builder):
    record = builder.build()
    assert isinstance(record, Record)


def test_build_raises_if_name_invalid(base_record):
    base_record.name.value = " "
    builder = RecordBuilder(base_record)
    with pytest.raises(InvalidException, match="Record must have a name before building"):
        builder.build()


# --- ADD PHONE --- #

def test_add_phone_success(builder):
    builder.add_phone("+380987654321")
    assert any(p.value == "+380987654321" for p in builder._record.phones)


def test_add_phone_object(builder):
    phone = Phone("+380555555555")
    builder.add_phone(phone)
    assert any(p.value == "+380555555555" for p in builder._record.phones)


def test_add_phone_duplicate_raises(builder):
    existing_phone = builder._record.phones[0].value
    with pytest.raises(AlreadyExistException, match="already has phone"):
        builder.add_phone(existing_phone)


# --- UPDATE PHONE --- #

def test_update_phone_success(builder):
    old = builder._record.phones[0].value
    builder.update_phone(old, "+380111111111")
    assert any(p.value == "+380111111111" for p in builder._record.phones)
    assert not any(p.value == old for p in builder._record.phones)


def test_update_phone_not_found_raises(builder):
    with pytest.raises(NotFoundException):
        builder.update_phone("999999", "000000")


# --- REMOVE PHONE --- #

def test_remove_phone_success(builder):
    phone = builder._record.phones[0].value
    builder.remove_phone(phone)
    assert all(p.value != phone for p in builder._record.phones)


def test_remove_phone_not_found(builder):
    with pytest.raises(NotFoundException):
        builder.remove_phone("nope")


# --- CLEAR PHONES --- #

def test_clear_phones(builder):
    builder.add_phone("+380111111111")
    builder.add_phone("+380222222222")
    builder.clear_phones()
    assert builder._record.phones == []


# --- BIRTHDAY --- #

def test_set_birthday_from_str(builder):
    builder.set_birthday("2000-05-20")
    assert isinstance(builder._record.birthday, Birthday)
    assert builder._record.birthday.value == date(2000, 5, 20)


def test_set_birthday_from_date(builder):
    bday = date(1999, 1, 1)
    builder.set_birthday(bday)
    assert builder._record.birthday.value == bday


def test_set_birthday_from_datetime(builder):
    bday = datetime(2005, 7, 15, 14, 0)
    builder.set_birthday(bday)
    assert builder._record.birthday.value == date(2005, 7, 15)


def test_clear_birthday(builder):
    builder.set_birthday("1990-01-01")
    builder.clear_birthday()
    assert builder._record.birthday is None
