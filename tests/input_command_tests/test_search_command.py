import pytest

from bll.registries.file_service_registry import FileServiceRegistry
from bll.services.command_service.command_service import CommandService
from bll.services.input_service.input_service import InputService
from bll.services.note_service.note_service import NoteService
from bll.services.record_service.record_service import RecordService
from dal.storages.address_book_storage import AddressBookStorage
from dal.storages.note_storage import NoteStorage


class FakeFileService:
    def is_save_able(self):
        return False

    def save_with_name(self, name="autosave"):
        return name

    def load_by_name(self, name):
        pass

    def delete_by_name(self, name):
        pass

    def get_file_list(self):
        return []


@pytest.fixture
def bot():
    record_storage = AddressBookStorage()
    note_storage = NoteStorage()

    record_service = RecordService(record_storage)
    note_service = NoteService(note_storage)

    contact_files = FakeFileService()
    note_files = FakeFileService()

    registry = FileServiceRegistry(contact_files, note_files)

    input_service = InputService()
    command_service = CommandService(
        record_service=record_service,
        note_service=note_service,
        input_service=input_service,
        file_service_registry=registry,
    )

    input_service.command_service = command_service
    return input_service, command_service


def test_search_contacts_flow(bot):
    input_service, command_service = bot

    cmd, args = input_service.handle("add-contact John +380991112233")
    command_service.execute(cmd, args)

    cmd, args = input_service.handle("add-contact Jane +380665554433")
    command_service.execute(cmd, args)

    cmd, args = input_service.handle("add-birthday John 05.11.2000")
    command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts john")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts 1122")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts 2000")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts not-found")
    assert "No contacts found" in command_service.execute(cmd, args)
