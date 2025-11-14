import pytest

from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.storages.NoteStorage import NoteStorage
from dal.exceptions.ExitBotException import ExitBotException
from bll.registries.FileServiceRegistry import FileServiceRegistry


class FakeFileService:
    """A lightweight simulation of PickleFileService for testing bot flow."""

    def __init__(self):
        self.files = {}
        self._saveable = False  # mimic is_save_able() check
        self.loaded = None

    def is_save_able(self) -> bool:
        return self._saveable

    def save_with_name(self, name: str = "autosave") -> str:
        """Simulate saving by storing filename in dict."""
        self.files[name] = True
        return name

    def load_by_name(self, name: str) -> bool:
        """Simulate successful load."""
        self.loaded = name
        return True

    def delete_by_name(self, name: str):
        """Simulate file deletion."""
        self.files.pop(name, None)

    def get_file_list(self):
        """Return the list of saved files."""
        return list(self.files.keys()) or ["autosave_test"]

    def get_latest_file_name(self):
        """Simulate getting the latest file name."""
        if self.files:
            return next(iter(self.files.keys()))
        return None


@pytest.fixture
def full_bot():
    """Creates a full working bot with fake file services."""

    contact_storage = AddressBookStorage()
    note_storage = NoteStorage()

    record_service = RecordService(contact_storage)
    note_service = NoteService(note_storage)

    # Fake file services for both contacts and notes
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

    # Bidirectional link (used for prompting inside CommandService)
    input_service.command_service = command_service

    return input_service, command_service, record_service, note_service, registry


def test_full_bot_flow(full_bot):
    input_service, command_service, record_service, note_service, registry = full_bot

    def run(cmd: str):
        command, args = input_service.handle(cmd)
        return command_service.execute(command, args)

    #
    # CONTACTS
    #
    assert "John" in run("add-contact John +380991112233")
    assert "Jane" in run("add-contact Jane +380987654321")

    assert "updated" in run("add-birthday John 05.11.2000")
    assert "updated" in run("add-birthday Jane 29.02.1996")

    assert "2000" in run("show-birthday John")

    assert "updated" in run("add-phone John +380990001122")
    assert len(record_service.get_by_name("John").phones) == 2

    assert "John" in run("show-all-contacts")

    assert isinstance(run("upcoming-birthdays"), str)

    assert "available" in run("help").lower()
    assert "help" in run("hello").lower()

    #
    # NOTES
    #
    command_service.input_service.read_value = lambda *a, **k: "My Title"
    command_service.input_service.read_multiline = lambda *a, **k: "Some content"

    assert "Note added" in run("add-note my_note")
    assert note_service.has("my_note")

    command_service.input_service.read_value = lambda *a, **k: "Updated Title"
    assert "updated" in run("edit-note-title my_note")

    command_service.input_service.read_multiline = lambda *a, **k: "Updated content"
    assert "updated" in run("edit-note-content my_note")

    #
    # EXIT — ensure it triggers saving through registry
    #
    registry._services["contacts"]._saveable = True
    registry._services["notes"]._saveable = True

    with pytest.raises(ExitBotException):
        run("exit")

    # validate save was triggered on both
    assert registry._services["contacts"].files
    assert registry._services["notes"].files
