import pytest
from datetime import datetime, date, timedelta

from bll.services.command_service.CommandService import CommandService
from bll.helpers.DateHelper import DateHelper
from dal.entities.Record import Record
from dal.entities.Birthday import Birthday
from dal.exceptions.ExitBotException import ExitBotException
from bll.registries.FileServiceRegistry import FileServiceRegistry


# ================================
# Fake Entities
# ================================
class FakeField:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class FakeNote:
    def __init__(self, name="my_note", title="Old title", content="Old content"):
        self.name = FakeField(name)
        self.title = FakeField(title)
        self.content = FakeField(content)
        self.created_at = datetime.now()
        self.updated_at = None

    def update(self):
        return FakeNoteBuilder(self)


class FakeNoteBuilder:
    def __init__(self, note: FakeNote):
        self._note = note

    def set_name(self, value: str):
        self._note.name = FakeField(value)
        return self

    def set_title(self, value: str):
        self._note.title = FakeField(value)
        return self

    def set_content(self, value: str):
        self._note.content = FakeField(value)
        return self

    def build(self):
        if not self._note.updated_at or self._note.created_at > self._note.updated_at:
            self._note.updated_at = self._note.created_at
        return self._note


# ================================
# Fake Services
# ================================


class FakeNoteService:
    def __init__(self):
        self.notes = {}

    def add(self, name, title, content):
        note = FakeNote(name, title, content)
        self.notes[name] = note
        return note

    def get_by_name(self, name):
        return self.notes[name]

    def update(self, name, note):
        self.notes[name] = note

    def delete(self, name):
        self.notes.pop(name, None)

    def get_all(self):
        return list(self.notes.values())

    def has(self, name):
        return name in self.notes


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
        self.records.pop(name, None)

    def get_all(self):
        return list(self.records.values())

    def search(self, query):
        res = []
        for r in self.records.values():
            if query.lower() in str(r).lower():
                res.append(r)
        return res

    def has(self, name):
        return name in self.records

    def get_with_upcoming_birthdays(self, days=7):
        def within(r):
            if not r.birthday:
                return False
            return DateHelper.is_date_within_next_week(
                r.birthday.value, today=date.today(), days=days
            )

        return [r for r in self.records.values() if within(r)]


class FakeFileService:
    def __init__(self):
        self.saved = []
        self.loaded = []
        self.deleted = []
        self.files = ["file1.pkl", "file2.pkl"]
        self._saveable = False

    def is_save_able(self):
        return self._saveable

    def save_with_name(self, name=None):
        result = name or "autosave"
        self.saved.append(result)
        return result

    def load_by_name(self, name):
        self.loaded.append(name)

    def delete_by_name(self, name):
        self.deleted.append(name)

    def get_file_list(self):
        return self.files


class FakeInputService:
    def __init__(self):
        self.next_value = None
        self.next_multiline = None

    def read_value(self, *args, **kwargs):
        return self.next_value

    def read_multiline(self, *args, **kwargs):
        return self.next_multiline


# ================================
# Fixtures
# ================================


@pytest.fixture
def fake_record_service():
    return FakeRecordService()


@pytest.fixture
def fake_contact_file_service():
    return FakeFileService()


@pytest.fixture
def fake_note_file_service():
    return FakeFileService()


@pytest.fixture
def fake_note_service():
    return FakeNoteService()


@pytest.fixture
def fake_input_service():
    return FakeInputService()


@pytest.fixture
def command_service(
    fake_record_service,
    fake_contact_file_service,
    fake_note_file_service,
    fake_note_service,
    fake_input_service,
):
    registry = FileServiceRegistry(fake_contact_file_service, fake_note_file_service)

    return CommandService(
        record_service=fake_record_service,
        note_service=fake_note_service,
        input_service=fake_input_service,
        file_service_registry=registry,
    )


# =============================================
# TESTS START
# =============================================


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
    assert isinstance(fake_record_service.records["John"].birthday, Birthday)


def test_show_birthday(command_service, fake_record_service):
    rec = Record("John", "+380991112233", birthday="05.11.2000")
    fake_record_service.save(rec)

    result = command_service.show_birthday(["John"])
    assert "05.11.2000" in result


def test_birthdays(command_service, fake_record_service):
    dt = date.today() + timedelta(days=1)
    bday = dt.replace(year=2000).strftime("%d.%m.%Y")
    rec = Record("John", "+380991112233", birthday=bday)
    fake_record_service.save(rec)

    result = command_service.birthdays()
    assert "John" in result
    assert bday in result


def test_birthdays_empty(command_service):
    result = command_service.birthdays()
    assert "No birthdays" in result


def test_birthdays_with_days_param(command_service, fake_record_service):
    near_dt = date.today() + timedelta(days=2)
    far_dt = date.today() + timedelta(days=10)

    near = near_dt.replace(year=2000).strftime("%d.%m.%Y")
    far = far_dt.replace(year=2000).strftime("%d.%m.%Y")

    fake_record_service.save(Record("Near", "+380991112233", birthday=near))
    fake_record_service.save(Record("Far", "+380665554433", birthday=far))

    result = command_service.birthdays(["5"])
    assert "Near" in result
    assert "Far" not in result


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


def test_exit_bot_no_save(command_service, fake_contact_file_service):
    fake_contact_file_service._saveable = False
    with pytest.raises(ExitBotException):
        command_service.exit_bot()


def test_exit_bot_with_save(command_service, fake_contact_file_service):
    fake_contact_file_service._saveable = True
    with pytest.raises(ExitBotException):
        command_service.exit_bot()


def test_delete_contact(command_service, fake_record_service):
    fake_record_service.save(Record("John", "+380991112233"))
    result = command_service.delete_contact(["John"])
    assert "deleted" in result.lower()
    assert not fake_record_service.has("John")


def test_save_state_with_name(command_service, fake_contact_file_service):
    res = command_service.save_contact_state(["manual"])
    assert "manual" in res
    assert "manual" in fake_contact_file_service.saved


def test_save_state_without_name(command_service, fake_contact_file_service):
    res = command_service.save_contact_state([])
    assert "autosave" in res
    assert "autosave" in fake_contact_file_service.saved


def test_load_state(command_service, fake_contact_file_service):
    res = command_service.load_contact_state(["manual"])
    assert "manual" in res
    assert "manual" in fake_contact_file_service.loaded


def test_delete_file(command_service, fake_contact_file_service):
    res = command_service.delete_contact_file(["trash.pkl"])
    assert "trash.pkl" in res
    assert "trash.pkl" in fake_contact_file_service.deleted


def test_show_all_files(command_service, fake_contact_file_service):
    res = command_service.show_contact_files()
    assert "file1.pkl" in res
    assert "file2.pkl" in res


def test_get_command_exists(command_service):
    assert command_service.get_command("add-contact") is not None


def test_get_command_missing(command_service):
    assert command_service.get_command("not-a-command") is None


def test_add_note(command_service, fake_note_service, fake_input_service):
    fake_input_service.next_value = "My Title"
    fake_input_service.next_multiline = "Long enough content"

    result = command_service.add_note(["my_note"])
    assert "Note added" in result
    assert fake_note_service.has("my_note")
    assert fake_note_service.notes["my_note"].title.value == "My Title"


def test_edit_note_title(command_service, fake_note_service, fake_input_service):
    fake_note_service.add("my_note", "Old title", "content")
    fake_input_service.next_value = "New title"

    result = command_service.edit_note_title(["my_note"])
    assert "New title" in result
    assert fake_note_service.get_by_name("my_note").title.value == "New title"


def test_edit_note_content(command_service, fake_note_service, fake_input_service):
    fake_note_service.add("my_note", "Title", "Old content")
    fake_input_service.next_multiline = "New multiline content"

    result = command_service.edit_note_content(["my_note"])
    assert "updated" in result.lower()
    assert (
        fake_note_service.get_by_name("my_note").content.value
        == "New multiline content"
    )
