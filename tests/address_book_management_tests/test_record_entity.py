import pytest
from datetime import date, datetime

from dal.entities.Record import Record
from dal.entities.Phone import Phone
from dal.entities.Birthday import Birthday
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException


# --- BASIC INITIALIZATION --- #

def test_create_record_with_multiple_phones():
    record = Record("John", "+380991112233", "+380665554433")
    assert record.name.value == "John"
    assert len(record.phones) == 2
    assert all(isinstance(p, Phone) for p in record.phones)
    assert record.birthday is None


def test_create_record_with_birthday():
    record = Record("Jane", "+380931234567", birthday="05.05.2000")
    assert record.name.value == "Jane"
    assert isinstance(record.birthday, Birthday)
    assert record.birthday.value == date(2000, 5, 5)


def test_record_str_representation():
    record = Record("John", "+380991112233", birthday="01.01.1990")
    text = str(record)
    assert "John" in text
    assert "+380991112233" in text
    assert "1990" in text


# --- EQUALITY CHECKS --- #

def test_record_equality_by_value():
    r1 = Record("John", "+380991112233")
    r2 = Record("John", "+380991112233")
    r3 = Record("Jane", "+380991112233")

    assert r1 == r2
    assert r1 != r3
    assert r1 == "John"
    assert r1 != "Jane"


def test_record_not_equal_to_other_type():
    r = Record("John", "+380991112233")
    assert (r == 123) is False  # should not crash


# --- PHONE LOGIC --- #

def test_has_phone_success():
    record = Record("John", "+380991112233")
    assert record.has_phone("+380991112233")


def test_has_phone_raises_on_none():
    record = Record("John")
    with pytest.raises(InvalidException):
        record.has_phone(None)


def test_find_phone_returns_phone_object():
    record = Record("John", "+380991112233")
    phone = record.find_phone("+380991112233")
    assert isinstance(phone, Phone)
    assert phone.value == "+380991112233"


def test_find_phone_raises_if_missing():
    record = Record("John", "+380991112233")
    with pytest.raises(NotFoundException):
        record.find_phone("+380931234567")


# --- UPDATE BUILDER --- #

def test_update_returns_record_builder_instance():
    record = Record("John", "+380991112233")
    builder = record.update()
    from dal.entity_builders.record_builder.RecordBuilder import RecordBuilder
    assert isinstance(builder, RecordBuilder)
    assert builder._record is record
