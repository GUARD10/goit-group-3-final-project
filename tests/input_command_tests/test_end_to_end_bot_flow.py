import pytest
from bll.services.input_service.InputService import InputService
from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.entities.Note import Note
from dal.entities.Tag import Tag
from dal.exceptions.ExitBotException import ExitBotException


# =========================
# Fake services
# =========================


class FakeFileService:
    def __init__(self):
        self.files = {}
        self._saveable = False

    def is_save_able(self):
        return self._saveable

    def save_with_name(self, name="autosave"):
        self.files[name] = "data"
        return name

    def load_by_name(self, name):
        if name not in self.files:
            raise Exception(f"File {name} not found")

    def delete_by_name(self, name):
        self.files.pop(name, None)

    def get_file_list(self):
        return list(self.files.keys()) or ["autosave_test"]


class FakeNoteService:
    def __init__(self):
        self.notes = {}

    def add(self, name: str, title: str, content: str) -> Note:
        note = Note(name, title, content)
        self.notes[name] = note
        return note

    def get_by_name(self, name: str) -> Note:
        return self.notes[name]

    def update(self, old_name: str, updated_note: Note) -> None:
        self.notes[old_name] = updated_note

    def has(self, name: str) -> bool:
        return name in self.notes

    def add_tags(self, note_name: str, tags: list[tuple[str, str | None]]):
        note = self.get_by_name(note_name)
        existing = {tag.value.lower(): tag for tag in note.tags}
        for name, color in tags:
            existing[name.lower()] = Tag(name, color)
        note.tags = list(existing.values())
        return note

    def remove_tag(self, note_name: str, tag_name: str):
        note = self.get_by_name(note_name)
        note.tags = [
            tag for tag in note.tags if tag.value.lower() != tag_name.lower()
        ]
        return note

    def get_distinct_tags(self):
        seen: dict[str, Tag] = {}
        for note in self.notes.values():
            for tag in note.tags:
                key = tag.value.lower()
                if key not in seen:
                    seen[key] = Tag(tag.value, tag.color)
        return sorted(seen.values(), key=lambda t: t.value.lower())

    def get_all_sorted_by_tags(self, tag_name: str | None = None):
        notes = list(self.notes.values())
        if tag_name:
            normalized = tag_name.lower()
            notes = [
                note
                for note in notes
                if any(tag.value.lower() == normalized for tag in note.tags)
            ]
        return notes


# =========================
# Fixtures
# =========================


@pytest.fixture
def full_bot():
    storage = AddressBookStorage()
    record_service = RecordService(storage)
    file_service = FakeFileService()
    note_service = FakeNoteService()
    input_service = InputService()

    command_service = CommandService(
        record_service, file_service, note_service, input_service
    )

    return input_service, command_service, record_service, note_service


# =========================
# Updated full bot test
# =========================


def test_full_bot_flow(full_bot):
    input_service, command_service, record_service, note_service = full_bot

    # helper executor
    def run(cmd: str) -> str:
        command, args = input_service.handle(cmd)
        return command_service.execute(command, args)

    # 1️⃣ Add contacts
    result = run("add-contact John +380991112233")
    assert "John" in result

    result = run("add-contact Jane +380987654321")
    assert "Jane" in result

    # 2️⃣ Add birthdays
    result = run("add-birthday John 05.11.2000")
    assert "updated" in result.lower()

    result = run("add-birthday Jane 29.02.1996")
    assert "updated" in result.lower()

    # 3️⃣ Show birthday
    result = run("show-birthday John")
    assert "2000" in result

    # 4️⃣ Add phone to John
    result = run("add-phone John +380990001122")
    john = record_service.get_by_name("John")
    assert len(john.phones) == 2

    # 5️⃣ Show all
    res = run("show-all-contacts")
    assert "John" in res and "Jane" in res

    # 6️⃣ Check birthdays
    res = run("upcoming-birthdays")
    assert isinstance(res, str)

    # 7️⃣ Help
    res = run("help")
    assert "available commands" in res.lower()

    # 8️⃣ Hello
    res = run("hello")
    assert "how can i help" in res.lower()

    # =============================
    # Notes subsystem tests 📝
    # =============================

    # 9️⃣ Add note
    # monkeypatch input in read_value + read_multiline
    # but test full flow → simulate values directly
    note_inputs = iter(["My Title", ""])
    command_service.input_service.read_value = (
        lambda *a, **k: next(note_inputs, "")
    )
    command_service.input_service.read_multiline = lambda *a, **k: "My content here"
    command_service.input_service.choose_multiple_from_list = (
        lambda *a, **k: []
    )
    command_service.input_service.choose_from_list = (
        lambda *a, **k: "__auto__"
    )

    result = run("add-note my_note")
    assert "Note added" in result or "success" in result.lower()
    assert note_service.has("my_note")

    # 🔟 Edit title
    command_service.input_service.read_value = lambda *a, **k: "Updated Title"

    result = run("edit-note-title my_note")
    assert "updated" in result.lower()
    assert note_service.get_by_name("my_note").title.value == "Updated Title"

    # 1️⃣1️⃣ Edit content
    command_service.input_service.read_multiline = lambda **kw: "New edited content"

    result = run("edit-note-content my_note")
    assert "updated" in result.lower()
    assert note_service.get_by_name("my_note").content.value == "New edited content"

    # =============================
    # Exit
    # =============================
    with pytest.raises(ExitBotException):
        run("exit")

    # Final validation
    all_records = record_service.get_all()
    assert len(all_records) == 2

    assert record_service.get_by_name("John").birthday.value.year == 2000
    assert record_service.get_by_name("Jane").birthday.value.year == 1996
