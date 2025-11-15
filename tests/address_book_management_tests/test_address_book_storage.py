import pytest

from dal.entities.record import Record
from dal.exceptions.invalid_error import InvalidError
from dal.storages.address_book_storage import AddressBookStorage


@pytest.fixture
def storage():
    return AddressBookStorage()


def test_add_and_find_record(storage):
    rec = Record("John", "+380991112233")
    storage.add(rec)
    found = storage.find("John")
    assert found == rec
    assert found.name.value == "John"
    assert found.phones[0].value == "+380991112233"


def test_update_record(storage):
    rec = Record("John", "+380991112233")
    storage.add(rec)
    new_rec = Record("John", "+380987654321")
    updated = storage.update_item("John", new_rec)
    assert updated.phones[0].value == "+380987654321"
    assert storage.find("John").phones[0].value == "+380987654321"


def test_delete_record(storage):
    rec = Record("Jane", "+380931234567")
    storage.add(rec)
    assert storage.has("Jane")
    storage.delete("Jane")
    assert not storage.has("Jane")
    assert storage.find("Jane") is None


def test_all_values(storage):
    storage.add(Record("A", "+380991112233"))
    storage.add(Record("B", "+380987654321"))
    values = storage.all_values()
    names = [v.name.value for v in values]
    assert len(values) == 2
    assert "A" in names and "B" in names


def test_has_method(storage):
    rec = Record("John", "+380991112233")
    storage.add(rec)
    assert storage.has("John")
    assert not storage.has("Ghost")


def test_filter_records(storage):
    storage.add(Record("A", "+380991112233"))
    storage.add(Record("B", "+380987654321"))
    result = storage.filter(lambda r: "9911" in r.phones[0].value)
    assert len(result) == 1
    assert result[0].name.value == "A"


def test_export_and_import_state(storage):
    r1 = Record("John", "+380991112233")
    r2 = Record("Jane", "+380987654321")
    storage.add(r1)
    storage.add(r2)

    exported = storage.export_state()
    assert isinstance(exported, dict)
    assert "John" in exported and "Jane" in exported

    # Імпорт нового стану
    new_state = {
        "Mike": Record("Mike", "+380931234567"),
        "Eva": Record("Eva", "+380930000000"),
    }
    storage.import_state(new_state)
    assert storage.has("Mike")
    assert not storage.has("John")
    assert len(storage.all_values()) == 2


def test_import_invalid_state_type_raises(storage):
    with pytest.raises(InvalidError):
        storage.import_state(["not", "a", "dict"])









