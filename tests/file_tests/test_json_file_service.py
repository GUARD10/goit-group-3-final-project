"""Integration tests for JSON backend with the existing file service."""
from pathlib import Path
from datetime import date

from bll.services.file_service.FileService import FileService
from dal.file_managers.json_file_manager.JsonFileManager import JsonFileManager
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.storages.NoteStorage import NoteStorage
from dal.entities.Record import Record
from dal.entities.Note import Note


class TestJsonFileService:
    def test_save_load_contacts_with_json_backend(self, tmp_path):
        base_dir = tmp_path / "contacts_json"
        manager = JsonFileManager[dict[str, Record]](base_dir)
        storage = AddressBookStorage()

        # Prepare storage
        storage.add(Record("Alice", "1234567890", birthday=date(1990, 1, 15)))
        storage.add(Record("Bob", "0987654321"))

        service = FileService[dict[str, Record]](manager, storage)

        # Save
        saved_name = service.save_with_name("contacts_backup")
        # Verify physically saved JSON exists (regardless of returned name format)
        assert any(name.endswith(".json") for name in manager.get_all_names())

        # Discover files via service
        names = service.get_file_list()
        assert any(name.endswith(".json") for name in names)

        # Load back into a fresh storage
        new_storage = AddressBookStorage()
        new_service = FileService[dict[str, Record]](manager, new_storage)
        latest = new_service.get_latest_file_name()
        new_service.load_by_name(latest)

        assert new_storage.has("Alice")
        assert new_storage.has("Bob")
        assert new_storage.find("Alice").phones[0].value == "1234567890"

    def test_save_load_notes_with_json_backend(self, tmp_path):
        base_dir = tmp_path / "notes_json"
        manager = JsonFileManager[dict[str, Note]](base_dir)
        storage = NoteStorage()

        # Prepare storage
        storage.add(Note("n1", "Title 1", "This is some content long enough."))
        storage.add(Note("n2", "Title 2", "Another content long enough."))

        service = FileService[dict[str, Note]](manager, storage)
        saved_name = service.save_with_name("notes_backup")

        # Ensure JSON file exists
        assert any(name.endswith(".json") for name in manager.get_all_names())

        # Modify storage and check is_save_able
        storage.add(Note("n3", "Title 3", "Content long enough here."))
        assert service.is_save_able() is True

        # Load back into fresh storage
        fresh = NoteStorage()
        fresh_service = FileService[dict[str, Note]](manager, fresh)
        fresh_service.load_by_name(fresh_service.get_latest_file_name())
        assert len(fresh.all_values()) >= 2
