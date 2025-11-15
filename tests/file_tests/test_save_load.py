from datetime import date

import pytest

from bll.services.file_service.file_service import FileService
from dal.entities.note import Note
from dal.entities.record import Record
from dal.file_managers.pickle_file_manager.pickle_file_manager import PickleFileManager
from dal.storages.address_book_storage import AddressBookStorage
from dal.storages.note_storage import NoteStorage


@pytest.fixture
def temp_dirs(tmp_path):
    contacts_dir = tmp_path / "contacts"
    notes_dir = tmp_path / "notes"

    contacts_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    return {"contacts": contacts_dir, "notes": notes_dir}


def test_contacts_and_notes_save_load(temp_dirs):
    contact_storage = AddressBookStorage()
    note_storage = NoteStorage()

    contact_manager = PickleFileManager[dict[str, Record]](temp_dirs["contacts"])
    note_manager = PickleFileManager[dict[str, Note]](temp_dirs["notes"])

    contact_service = FileService(contact_manager, contact_storage)
    note_service = FileService(note_manager, note_storage)

    # Тестові дані
    r1 = Record("Alice", "+380991112233").update().set_birthday("01.01.2000").build()
    r2 = Record("Bob", "+380992223344").update().add_phone("+380955553333").build()
    contact_storage.add(r1)
    contact_storage.add(r2)

    n1 = Note("note1", "Title A", "Content AAAA long text")
    n2 = Note("note2", "Title B", "Some long enough content here")
    note_storage.add(n1)
    note_storage.add(n2)

    # Збереження
    contacts_file = contact_service.save_with_name("contacts_backup")
    notes_file = note_service.save_with_name("notes_backup")

    assert (temp_dirs["contacts"] / contacts_file).exists()
    assert (temp_dirs["notes"] / notes_file).exists()

    # Очищення сховищ
    contact_storage.data.clear()
    note_storage.data.clear()

    assert len(contact_storage.data) == 0
    assert len(note_storage.data) == 0

    # Завантаження
    contact_service.load_by_name(contacts_file)
    note_service.load_by_name(notes_file)

    # Перевірка
    assert "Alice" in contact_storage.data
    assert "Bob" in contact_storage.data

    loaded_r1 = contact_storage.data["Alice"]
    assert loaded_r1.name.value == "Alice"
    assert loaded_r1.birthday.value == date(2000, 1, 1)

    loaded_n1 = note_storage.data["note1"]
    assert loaded_n1.content.value.startswith("Content AAAA")









