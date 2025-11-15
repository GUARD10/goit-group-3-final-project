# tests/conftest.py

import pytest

from bll.registries.file_service_registry import FileServiceRegistry
from bll.services.command_service.command_service import CommandService
from bll.services.input_service.input_service import InputService
from bll.services.note_service.note_service import NoteService
from bll.services.record_service.record_service import RecordService
from dal.storages.address_book_storage import AddressBookStorage
from dal.storages.note_storage import NoteStorage


class FakeFileService:
    def __init__(self):
        self.files = {}
        self._saveable = False
        self.loaded = None

    def is_save_able(self):
        return self._saveable

    def save_with_name(self, name="autosave"):
        self.files[name] = True
        return name

    def load_by_name(self, name):
        self.loaded = name
        return True

    def delete_by_name(self, name):
        self.files.pop(name, None)

    def get_file_list(self):
        return list(self.files.keys()) or ["autosave_test"]


@pytest.fixture
def full_bot():
    contact_storage = AddressBookStorage()
    note_storage = NoteStorage()

    record_service = RecordService(contact_storage)
    note_service = NoteService(note_storage)

    fake_contacts = FakeFileService()
    fake_notes = FakeFileService()

    registry = FileServiceRegistry(fake_contacts, fake_notes)

    input_service = InputService()

    # override ALL interactive methods to avoid loops
    input_service.read_value = lambda *a, **k: "mocked"
    input_service.read_multiline = lambda *a, **k: "mocked content long enough"
    input_service.choose_multiple_from_list = lambda *a, **k: []
    input_service.choose_from_list = lambda *a, **k: "__auto__"

    command_service = CommandService(
        record_service=record_service,
        note_service=note_service,
        input_service=input_service,
        file_service_registry=registry,
    )

    input_service.command_service = command_service

    return input_service, command_service, record_service, note_service, registry









