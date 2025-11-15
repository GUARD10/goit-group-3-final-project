import pytest

from bll.services.record_service.record_service import RecordService
from dal.entities.record import Record
from dal.exceptions.invalid_error import InvalidError
from dal.storages.address_book_storage import AddressBookStorage


@pytest.fixture
def service():
    return RecordService(AddressBookStorage())


def setup_data(service: RecordService):
    service.save(Record("John Doe", "+380991112233", birthday="05.11.2000"))
    service.save(Record("Jane Smith", "+380665554433", birthday="29.02.1996"))


def test_search_by_name(service):
    setup_data(service)
    res = service.search("john")
    assert len(res) == 1
    assert res[0].name.value == "John Doe"


def test_search_by_partial_phone(service):
    setup_data(service)
    res = service.search("1122")
    assert any(r.name.value == "John Doe" for r in res)


def test_search_by_birthday_fragment(service):
    setup_data(service)
    res = service.search("2000")
    assert any(r.name.value == "John Doe" for r in res)


def test_search_multiple_terms_and_case_insensitive(service):
    setup_data(service)
    res = service.search("JoHn 1223")
    assert len(res) == 1
    assert res[0].name.value == "John Doe"


def test_search_no_results(service):
    setup_data(service)
    res = service.search("not-existing")
    assert res == []


def test_search_empty_query_raises(service):
    with pytest.raises(InvalidError):
        service.search("  ")
