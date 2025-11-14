# tests/conftest.py

import pytest

from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.storages.NoteStorage import NoteStorage
from bll.registries.FileServiceRegistry import FileServiceRegistry


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
