import pytest

from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService

from dal.storages.AddressBookStorage import AddressBookStorage
from dal.storages.NoteStorage import NoteStorage


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
    contact_storage = AddressBookStorage()
    note_storage = NoteStorage()

    record_service = RecordService(contact_storage)
    note_service = NoteService(note_storage)
    file_service = FakeFileService()

    input_service = InputService()
    command_service = CommandService(
        record_service=record_service,
        file_service=file_service,
        note_service=note_service,
        input_service=input_service,
    )

    # 🔁 Додаємо посилання назад
    input_service.command_service = command_service

    # Повертаємо обидва сервіси
    return input_service, command_service


def test_search_contacts_flow(bot):
    input_service, command_service = bot

    cmd, args = input_service.handle("add-contact John +380991112233")
    assert "Contact added" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("add-contact Jane +380665554433")
    assert "Contact added" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("add-birthday John 05.11.2000")
    assert "Contact updated" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts john")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts 1122")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts 2000")
    assert "John" in command_service.execute(cmd, args)

    cmd, args = input_service.handle("search-contacts not-found")
    assert "No matching contacts" in command_service.execute(cmd, args)
