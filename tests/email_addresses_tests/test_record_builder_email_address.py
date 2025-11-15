from datetime import date, datetime

import pytest

from bll.entity_builders.record_builder.record_builder import RecordBuilder
from dal.entities.address import Address
from dal.entities.birthday import Birthday
from dal.entities.email import Email
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.not_found_error import NotFoundError


@pytest.fixture
def base_record():
    # без email та address за замовчуванням
    return Record("Roman", "+380931112233")


@pytest.fixture
def builder(base_record):
    return RecordBuilder(base_record)


# ---------- EMAIL: ADD ---------- #


def test_add_email_success(builder):
    builder.add_email("roman@example.com")
    assert len(builder._record.emails) == 1
    assert builder._record.emails[0].value == "roman@example.com"


def test_add_email_as_email_object(builder):
    email_obj = Email("roman@example.com")
    builder.add_email(email_obj)
    assert len(builder._record.emails) == 1
    assert builder._record.emails[0] is email_obj


def test_add_email_duplicate_raises(builder):
    builder.add_email("roman@example.com")
    with pytest.raises(AlreadyExistsError):
        builder.add_email("roman@example.com")


# ---------- EMAIL: UPDATE ---------- #


def test_update_email_success(builder):
    builder.add_email("old@example.com")
    builder.update_email("old@example.com", "new@example.com")

    values = [e.value for e in builder._record.emails]
    assert "new@example.com" in values
    assert "old@example.com" not in values
    assert len(builder._record.emails) == 1


def test_update_email_with_email_objects(builder):
    old = Email("old@example.com")
    new = Email("new@example.com")
    builder.add_email(old)
    builder.update_email(old, new)

    assert len(builder._record.emails) == 1
    assert builder._record.emails[0] == new


def test_update_email_old_not_found_raises(builder):
    builder.add_email("some@example.com")
    with pytest.raises(NotFoundError):
        builder.update_email("ghost@example.com", "new@example.com")


def test_update_email_new_already_exists_raises(builder):
    builder.add_email("first@example.com")
    builder.add_email("second@example.com")
    with pytest.raises(AlreadyExistsError):
        builder.update_email("first@example.com", "second@example.com")


# ---------- EMAIL: REMOVE ---------- #


def test_remove_existing_email(builder):
    builder.add_email("one@example.com")
    builder.add_email("two@example.com")

    builder.remove_email("one@example.com")
    values = [e.value for e in builder._record.emails]

    assert "one@example.com" not in values
    assert "two@example.com" in values
    assert len(builder._record.emails) == 1


def test_remove_email_with_email_object(builder):
    email_obj = Email("one@example.com")
    builder.add_email(email_obj)

    builder.remove_email(email_obj)
    assert builder._record.emails == []


def test_remove_nonexistent_email_raises(builder):
    builder.add_email("existing@example.com")
    with pytest.raises(NotFoundError):
        builder.remove_email("ghost@example.com")


# ---------- ADDRESS: SET / CLEAR ---------- #


def test_set_address_with_string(builder):
    builder.set_address("Kyiv, Main street 10")
    assert isinstance(builder._record.address, Address)
    assert builder._record.address.value == "Kyiv, Main street 10"


def test_set_address_with_address_object(builder):
    addr = Address("Lviv, Some street 5")
    builder.set_address(addr)
    assert builder._record.address is addr


def test_update_address_overwrites_previous(builder):
    builder.set_address("Old address")
    builder.set_address("New address")
    assert builder._record.address.value == "New address"


def test_clear_existing_address(builder):
    builder.set_address("Some address")
    builder.clear_address()
    assert builder._record.address is None


def test_clear_address_not_set_raises(builder):
    # address із самого початку None
    with pytest.raises(NotFoundError):
        builder.clear_address()


# ---------- BIRTHDAY ---------- #


def test_set_birthday_from_str(builder):
    builder.set_birthday("2000-05-20")
    assert isinstance(builder._record.birthday, Birthday)
    assert builder._record.birthday.value == date(2000, 5, 20)


def test_set_birthday_from_date(builder):
    d = date(1999, 12, 31)
    builder.set_birthday(d)
    assert builder._record.birthday.value == d


def test_set_birthday_from_datetime(builder):
    dt = datetime(1990, 1, 1, 10, 0)
    builder.set_birthday(dt)
    assert builder._record.birthday.value == date(1990, 1, 1)









