import pytest
from dal.entities.Note import Note
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.NoteStorage import NoteStorage
from bll.services.note_service.NoteService import NoteService


@pytest.fixture
def service():
    return NoteService(NoteStorage())


def test_add_note_success(service):
    note = service.add("n", "Title", "1234567890")
    assert note.name.value == "n"


def test_add_note_duplicate_raises(service):
    service.add("n", "T", "1234567890")
    with pytest.raises(AlreadyExistException):
        service.add("n", "T", "1234567890")


def test_add_note_invalid_fields(service):
    with pytest.raises(InvalidException):
        service.add("", "T", "1234567890")

    with pytest.raises(InvalidException):
        service.add("name", "", "1234567890")

    with pytest.raises(InvalidException):
        service.add("name", "T", 123)  # wrong type


def test_update_note(service):
    original = service.add("n", "T", "1234567890")
    original.content.value = "UPDATED CONTENT"

    updated = service.update("n", original)
    assert updated.content.value == "UPDATED CONTENT"


def test_update_nonexistent_note(service):
    with pytest.raises(NotFoundException):
        service.update("x", Note("x", "T", "1234567890"))


def test_get_by_name_success(service):
    service.add("n", "T", "1234567890")
    note = service.get_by_name("n")
    assert note.name.value == "n"


def test_get_by_name_missing(service):
    with pytest.raises(NotFoundException):
        service.get_by_name("missing")


def test_rename_note(service):
    service.add("n", "T", "1234567890")
    service.rename("n", "renamed")

    note = service.get_by_name("renamed")
    assert note.name.value == "renamed"


def test_rename_missing(service):
    with pytest.raises(NotFoundException):
        service.rename("x", "y")


def test_delete_note(service):
    service.add("n", "T", "1234567890")
    service.delete("n")
    assert not service.has("n")


def test_delete_missing(service):
    with pytest.raises(NotFoundException):
        service.delete("nope")
