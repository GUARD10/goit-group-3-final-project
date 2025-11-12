import pytest
from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from dal.Storages.AddressBookStorage import AddressBookStorage
from dal.entities.Record import Record
from dal.Exceptions.ExitBotException import ExitBotException


class FakeFileService:
    def __init__(self):
        self.files = {}

    def is_save_able(self):
        # Для тестів завжди False, щоб не викликати input()
        return False

    def save_with_name(self, name="autosave"):  # no-op
        self.files[name] = "data"

    def load_by_name(self, name):
        if name not in self.files:
            raise Exception(f"File {name} not found")

    def delete_by_name(self, name):
        self.files.pop(name, None)

    def get_file_list(self):
        return list(self.files.keys()) or ["autosave_test"]


@pytest.fixture
def full_bot():
    storage = AddressBookStorage()
    record_service = RecordService(storage)
    file_service = FakeFileService()
    command_service = CommandService(record_service, file_service)
    input_service = InputService(command_service)
    return input_service, record_service


def test_full_bot_flow(full_bot):
    input_service, record_service = full_bot

    # 1️⃣ Add 2 contacts
    result = input_service.handle("add-contact John +380991112233")
    assert "John" in result and "+380991112233" in result

    result = input_service.handle("add-contact Jane +380987654321")
    assert "Jane" in result and "+380987654321" in result

    # 2️⃣ Add birthdays
    result = input_service.handle("add-birthday John 05.11.2000")
    assert "contact updated" in result.lower()

    result = input_service.handle("add-birthday Jane 29.02.1996")
    assert "contact updated" in result.lower()

    # 3️⃣ Check birthdays
    result = input_service.handle("show-birthday John")
    assert "05.11.2000" in result or "2000-11-05" in result

    # 4️⃣ Add another phone to John
    result = input_service.handle("add-phone John +380990001122")
    john = record_service.get_by_name("John")
    assert len(john.phones) == 2
    assert any(p.value == "+380990001122" for p in john.phones)

    # 5️⃣ Show all contacts
    result = input_service.handle("show-all-contacts")
    assert "John" in result and "Jane" in result

    # 6️⃣ Show upcoming birthdays
    result = input_service.handle("upcoming-birthdays")
    assert isinstance(result, str)
    assert "contact" in result.lower() or "no birthdays" in result.lower()

    # 7️⃣ Show help
    result = input_service.handle("help")
    assert "available commands" in result.lower()
    assert "add-contact" in result.lower()
    assert "exit" in result.lower()

    # 8️⃣ Greeting
    result = input_service.handle("hello")
    assert "how can i help" in result.lower()

    # 9️⃣ Exit command
    with pytest.raises(ExitBotException):
        input_service.handle("exit")

    # 🔟 Final data validation
    all_records = record_service.get_all()
    assert len(all_records) == 2

    john = record_service.get_by_name("John")
    assert isinstance(john, Record)
    assert len(john.phones) == 2
    assert john.birthday is not None
    assert john.birthday.value.year == 2000

    jane = record_service.get_by_name("Jane")
    assert jane.birthday is not None
    assert jane.birthday.value.year == 1996
