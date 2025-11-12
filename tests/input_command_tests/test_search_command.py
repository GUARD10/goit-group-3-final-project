import pytest

from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from dal.storages.AddressBookStorage import AddressBookStorage


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
    storage = AddressBookStorage()
    rs = RecordService(storage)
    fs = FakeFileService()
    cs = CommandService(rs, fs)
    return InputService(cs)


def test_search_contacts_flow(bot):
    assert "Contact added" in bot.handle("add-contact John +380991112233")
    assert "Contact added" in bot.handle("add-contact Jane +380665554433")
    assert "Contact updated" in bot.handle("add-birthday John 05.11.2000")

    res = bot.handle("search-contacts john")
    assert "John" in res

    res = bot.handle("search-contacts 1122")
    assert "John" in res

    res = bot.handle("search-contacts 2000")
    assert "John" in res

    res = bot.handle("search-contacts not-found")
    assert "No matching contacts" in res
