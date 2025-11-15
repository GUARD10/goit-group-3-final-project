from datetime import date, timedelta

import pytest

from bll.services.record_service.record_service import RecordService
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError
from dal.storages.address_book_storage import AddressBookStorage


@pytest.fixture
def service():
    return RecordService(AddressBookStorage())


def test_save_and_get_by_name(service):
    record = Record("John", "1234567890")
    service.save(record)
    result = service.get_by_name("John")
    assert result == record
    assert result.name.value == "John"


def test_save_duplicate_raises(service):
    record = Record("John", "1234567890")
    service.save(record)
    with pytest.raises(AlreadyExistsError):
        service.save(Record("John", "1112223333"))


def test_update_record(service):
    old = Record("John", "1234567890")
    service.save(old)

    new = Record("John", "0987654321")
    updated = service.update("John", new)
    assert updated.phones[0].value == "0987654321"


def test_update_not_found_raises(service):
    with pytest.raises(NotFoundError):
        service.update("Ghost", Record("Ghost", "1111111111"))


def test_rename_record(service):
    record = Record("John", "1234567890")
    service.save(record)

    renamed = service.rename("John", "Johnny")
    assert renamed.name.value == "Johnny"
    assert not service.has("John")
    assert service.has("Johnny")


def test_delete_record(service):
    record = Record("Jane", "1112223333")
    service.save(record)
    assert service.has("Jane")

    service.delete("Jane")
    assert not service.has("Jane")


def test_delete_nonexistent(service):
    with pytest.raises(NotFoundError):
        service.delete("Ghost")


def test_get_all_records(service):
    service.save(Record("John", "1234567890"))
    service.save(Record("Jane", "0987654321"))
    all_records = service.get_all()
    assert len(all_records) == 2
    assert any(r.name.value == "Jane" for r in all_records)


def test_has_validation(service):
    with pytest.raises(InvalidError):
        service.has(None)
    with pytest.raises(InvalidError):
        service.has(123)


def test_get_with_upcoming_birthdays(service):
    today = date.today()
    near_bday = today.replace(year=2000) + timedelta(days=3)
    far_bday = today.replace(year=2000) + timedelta(days=30)
    last_week = today.replace(year=2000) - timedelta(days=5)

    service.save(Record("John", "1234567890", birthday=near_bday.strftime("%d.%m.%Y")))
    service.save(Record("Jane", "0987654321", birthday=far_bday.strftime("%d.%m.%Y")))
    service.save(Record("Mark", "1112223333", birthday=last_week.strftime("%d.%m.%Y")))

    upcoming = service.get_with_upcoming_birthdays()

    assert len(upcoming) == 1
    assert upcoming[0].name.value == "John"


def test_get_with_upcoming_birthdays_days_param(service):
    today = date.today()
    in_2 = today.replace(year=2000) + timedelta(days=2)
    in_8 = today.replace(year=2000) + timedelta(days=8)

    service.save(Record("Near", "1234567890", birthday=in_2.strftime("%d.%m.%Y")))
    service.save(Record("Far", "0987654321", birthday=in_8.strftime("%d.%m.%Y")))

    upcoming5 = service.get_with_upcoming_birthdays(days=5)
    names5 = [r.name.value for r in upcoming5]
    assert "Near" in names5 and "Far" not in names5
