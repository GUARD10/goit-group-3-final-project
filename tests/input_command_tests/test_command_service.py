import pytest
from datetime import datetime
from bll.services.command_service.CommandService import CommandService
from dal.entities.Record import Record
from dal.entities.Birthday import Birthday
from dal.exceptions.ExitBotException import ExitBotException


# === Fake dependencies ===

class FakeRecordService:
    def __init__(self):
        self.records = {}

    def save(self, record):
        self.records[record.name.value] = record

    def update(self, name, record):
        self.records[name] = record

    def get_by_name(self, name):
        return self.records.get(name)

    def delete(self, name):
        if name in self.records:
            del self.records[name]

    def get_all(self):
        return list(self.records.values())

    def get_with_upcoming_birthdays(self):
        return [r for r in self.records.values() if r.birthday]

    def has(self, name):
        return name in self.records


class FakeFileService:
    def __init__(self):
        self.saved = []
        self.loaded = []
        self.deleted = []
        self.files = ["file1.pkl", "file2.pkl"]
        self._saveable = False  # контроль для тестів

    def is_save_able(self):
        return self._saveable

    def save_with_name(self, name=None):
        self.saved.append(name or "autosave")
        return name or "autosave"

    def load_by_name(self, name):
        self.loaded.append(name)

    def delete_by_name(self, name):
        self.deleted.append(name)

    def get_file_list(self):
        return self.files


# === Fixtures ===

@pytest.fixture
def fake_record_service():
    return FakeRecordService()

@pytest.fixture
def fake_file_service():
    return FakeFileService()

@pytest.fixture
def command_service(fake_record_service, fake_file_service):
    return CommandService(fake_record_service, fake_file_service)


# === Tests ===

def test_add_contact(command_service, fake_record_service):
    result = command_service.add_contact(["John", "+380991112233"])
    assert "Contact added" in result
    assert "John" in fake_record_service.records


def test_add_phone(command_service, fake_record_service):
    rec = Record("John", "+380991112233")
    fake_record_service.save(rec)
    result = command_service.add_phone(["John", "+380111222333"])
    assert "Contact updated" in result
    assert len(fake_record_service.records["John"].phones) == 2


def test_show_phone(command_service, fake_record_service):
    rec = Record("John", "+380991112233", "+380665554433")
    fake_record_service.save(rec)
    result = command_service.show_phone(["John"])
    assert "+380991112233" in result
    assert "+380665554433" in result


def test_add_birthday(command_service, fake_record_service):
    rec = Record("John", "+380991112233")
    fake_record_service.save(rec)
    result = command_service.add_birthday(["John", "05.11.2000"])
    assert "Contact updated" in result
    assert isinstance(rec.birthday, Birthday)


def test_show_birthday(command_service, fake_record_service):
    rec = Record("John", "+380991112233", birthday="05.11.2000")
    fake_record_service.save(rec)
    result = command_service.show_birthday(["John"])
    assert "05.11.2000" in result


def test_birthdays(command_service, fake_record_service):
    rec = Record("John", "+380991112233", birthday="05.11.2000")
    fake_record_service.save(rec)
    result = command_service.birthdays()
    assert "John" in result
    assert "05.11.2000" in result


def test_birthdays_empty(command_service):
    result = command_service.birthdays()
    assert "No birthdays" in result


def test_show_all(command_service, fake_record_service):
    fake_record_service.save(Record("John", "+380991112233"))
    fake_record_service.save(Record("Jane", "+380665554433"))
    result = command_service.show_all()
    assert "John" in result and "Jane" in result


def test_show_all_empty(command_service):
    result = command_service.show_all()
    assert "No contacts" in result


def test_hello_and_help(command_service):
    assert "help" in command_service.help_command().lower()
    assert "how can i help" in command_service.hello().lower()


def test_exit_bot_no_save(command_service):
    """exit_bot when file_service.is_save_able() == False"""
    command_service.file_service._saveable = False
    with pytest.raises(ExitBotException):
        command_service.exit_bot()


def test_exit_bot_with_save(monkeypatch, command_service):
    """exit_bot when file_service.is_save_able() == True"""
    command_service.file_service._saveable = True
    # емулюємо відповідь користувача "n" на питання про збереження
    monkeypatch.setattr("builtins.input", lambda _: "n")
    with pytest.raises(ExitBotException):
        command_service.exit_bot()


def test_delete_contact(command_service, fake_record_service):
    rec = Record("John", "+380991112233")
    fake_record_service.save(rec)
    result = command_service.delete_contact(["John"])
    assert "deleted" in result.lower()
    assert not fake_record_service.has("John")


def test_save_state_with_name(command_service, fake_file_service):
    res = command_service.save_state(["manual"])
    assert "manual" in res
    assert "manual" in fake_file_service.saved


def test_save_state_without_name(command_service, fake_file_service):
    res = command_service.save_state([])
    assert "autosave" in res
    assert any("autosave" in s for s in fake_file_service.saved)


def test_load_state(command_service, fake_file_service):
    res = command_service.load_state(["manual"])
    assert "manual" in res
    assert "manual" in fake_file_service.loaded


def test_delete_file(command_service, fake_file_service):
    res = command_service.delete_file(["trash.pkl"])
    assert "trash.pkl" in res
    assert "trash.pkl" in fake_file_service.deleted


def test_show_all_files(command_service, fake_file_service):
    res = command_service.show_all_files()
    assert "file1.pkl" in res
    assert "file2.pkl" in res


def test_get_command_exists(command_service):
    cmd = command_service.get_command("add-contact")
    assert cmd is not None
    assert cmd.name == "add-contact"


def test_get_command_missing(command_service):
    assert command_service.get_command("not-a-command") is None
