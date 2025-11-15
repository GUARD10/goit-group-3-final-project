import pytest

from bll.services.note_service.note_service import NoteService
from dal.entities.note import Note
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError
from dal.storages.note_storage import NoteStorage


@pytest.fixture
def service():
    return NoteService(NoteStorage())


def test_add_note_success(service):
    note = service.add("n", "Title", "1234567890")
    assert note.name.value == "n"


def test_add_note_duplicate_raises(service):
    service.add("n", "T", "1234567890")
    with pytest.raises(AlreadyExistsError):
        service.add("n", "T", "1234567890")


def test_add_note_invalid_fields(service):
    with pytest.raises(InvalidError):
        service.add("", "T", "1234567890")

    with pytest.raises(InvalidError):
        service.add("name", "", "1234567890")

    with pytest.raises(InvalidError):
        service.add("name", "T", 123)  # wrong type


def test_update_note(service):
    original = service.add("n", "T", "1234567890")
    original.content.value = "UPDATED CONTENT"

    updated = service.update("n", original)
    assert updated.content.value == "UPDATED CONTENT"


def test_update_nonexistent_note(service):
    with pytest.raises(NotFoundError):
        service.update("x", Note("x", "T", "1234567890"))


def test_get_by_name_success(service):
    service.add("n", "T", "1234567890")
    note = service.get_by_name("n")
    assert note.name.value == "n"


def test_get_by_name_missing(service):
    with pytest.raises(NotFoundError):
        service.get_by_name("missing")


def test_rename_note(service):
    service.add("n", "T", "1234567890")
    service.rename("n", "renamed")

    note = service.get_by_name("renamed")
    assert note.name.value == "renamed"


def test_rename_missing(service):
    with pytest.raises(NotFoundError):
        service.rename("x", "y")


def test_delete_note(service):
    service.add("n", "T", "1234567890")
    service.delete("n")
    assert not service.has("n")


def test_delete_missing(service):
    with pytest.raises(NotFoundError):
        service.delete("nope")
