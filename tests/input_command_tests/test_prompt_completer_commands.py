from typing import cast

from prompt_toolkit.document import Document

from bll.helpers.prompt_completer import PromptCompleter
from bll.services.command_service.command_service import CommandService
from bll.services.note_service.note_service import NoteService
from bll.services.record_service.record_service import RecordService


class FakeCommand:
    def __init__(self, name: str):
        self.name = name
        self.handler = None
        self.description = ""


class FakeFileService:
    def __init__(self, files: list[str]):
        self._files = files

    def get_file_list(self) -> list[str]:
        return self._files


class FakeFileServiceRegistry:
    def __init__(self):
        self._services = {
            "contacts": FakeFileService(
                ["contacts_autosave_1.pkl", "contacts_backup.pkl"]
            ),
            "notes": FakeFileService(["notes_autosave_1.pkl", "notes_ideas.pkl"]),
        }

    def get(self, key: str):
        return self._services.get(key)


class FakeCommandService:
    def __init__(self):
        names = [
            "add-phone",
            "add-email",
            "delete-email",
            "set-address",
            "delete-address",
            "add-birthday",
            "show-birthday",
            "delete-contact",
            "search-contacts",
            "edit-note-title",
            "edit-note-content",
            "delete-note",
            "add-note-tags",
            "remove-note-tag",
            "show-notes-by-tag",
            # файли контактів
            "load-contact",
            "delete-contact-file",
            "contacts-files",
            # файли нотаток
            "load-note",
            "delete-note-file",
            "note-files",
            "help",
            "exit",
        ]

        self.commands = {name: FakeCommand(name) for name in names}
        # емулюємо те, що є в реальному CommandService
        self.file_service_registry = FakeFileServiceRegistry()


class FakeRecord:
    def __init__(self, name: str):
        # емулюємо dal.entities.Name
        self.name = type("N", (), {"value": name})
        self.phones: list[str] = []


class FakeRecordService:
    def __init__(self):
        self._records = [
            FakeRecord("Roman"),
            FakeRecord("John"),
            FakeRecord("Jane"),
        ]

    def get_all(self):
        return self._records


class FakeNote:
    def __init__(
        self, name: str, title: str | None = None, tags: list[str] | None = None
    ):
        # емулюємо note.name.value та note.title.value
        self.name = type("N", (), {"value": name})
        # title нам зараз не критично, але нехай буде для сумісності
        self.title = type("T", (), {"value": title or name})
        # емулюємо note.tags (список тегів без #)
        self.tags = tags or []


class FakeNoteService:
    def __init__(self):
        self._notes = [
            FakeNote("Shopping list", tags=["groceries", "todo"]),
            FakeNote("Work tasks", tags=["work", "urgent"]),
            FakeNote("Roman study plan", tags=["study", "todo"]),
            FakeNote("Roman", tags=["roman-tag", "todo"]),
        ]

    def get_all(self):
        return self._notes


def collect_completions(completer: PromptCompleter, text: str) -> list[str]:
    doc = Document(text=text, cursor_position=len(text))
    return [c.text for c in completer.get_completions(doc, None)]


def _make_completer() -> PromptCompleter:
    """
    Створюємо PromptCompleter з фейковими сервісами,
    але через cast кажемо mypy, що це ок.
    """
    return PromptCompleter(
        command_service=cast(CommandService, FakeCommandService()),
        record_service=cast(RecordService, FakeRecordService()),
        note_service=cast(NoteService, FakeNoteService()),
    )


def test_command_name_completion_by_prefix():
    completer = _make_completer()

    completions = collect_completions(completer, "add-")

    assert "add-phone" in completions
    assert "add-email" in completions
    assert "edit-note-title" not in completions


def test_contact_commands_suggest_contact_names():
    completer = _make_completer()

    completions = collect_completions(completer, "add-phone Ro")

    assert "Roman" in completions
    assert "John" not in completions


def test_note_title_commands_suggest_note_names():
    completer = _make_completer()

    completions = collect_completions(completer, "edit-note-title Ro")

    assert "Roman study plan" in completions
    assert "Shopping list" not in completions


def test_add_note_tags_suggests_all_tags_by_prefix():
    completer = _make_completer()

    completions = collect_completions(completer, "add-note-tags Roman study plan t")

    assert "todo" in completions
    assert "urgent" not in completions


def test_remove_note_tag_suggests_tags_for_specific_note():
    completer = _make_completer()

    completions = collect_completions(completer, "remove-note-tag Roman t")

    assert "todo" in completions
    assert "roman-tag" not in completions


def test_show_notes_by_tag_suggests_all_tags():
    completer = _make_completer()

    completions = collect_completions(completer, "show-notes-by-tag t")

    assert "todo" in completions
    assert "work" not in completions


def test_load_contact_suggests_contact_files():
    """
    load-contact [filename] має підказувати тільки файли контактів.
    """
    completer = _make_completer()

    completions = collect_completions(completer, "load-contact c")

    assert "contacts_autosave_1.pkl" in completions
    assert "contacts_backup.pkl" in completions
    # файли нотаток не мають з'являтися
    assert "notes_autosave_1.pkl" not in completions
    assert "notes_ideas.pkl" not in completions


def test_delete_contact_file_suggests_contact_files():
    """
    delete-contact-file [filename] має підказувати тільки файли контактів.
    """
    completer = _make_completer()

    completions = collect_completions(completer, "delete-contact-file c")

    assert "contacts_autosave_1.pkl" in completions
    assert "contacts_backup.pkl" in completions
    assert "notes_autosave_1.pkl" not in completions
    assert "notes_ideas.pkl" not in completions


def test_load_note_suggests_note_files():
    """
    load-note [filename] має підказувати тільки файли нотаток.
    """
    completer = _make_completer()

    completions = collect_completions(completer, "load-note n")

    assert "notes_autosave_1.pkl" in completions
    assert "notes_ideas.pkl" in completions
    assert "contacts_autosave_1.pkl" not in completions
    assert "contacts_backup.pkl" not in completions


def test_delete_note_file_suggests_note_files():
    """
    delete-note-file [filename] має підказувати тільки файли нотаток.
    """
    completer = _make_completer()

    completions = collect_completions(completer, "delete-note-file n")

    assert "notes_autosave_1.pkl" in completions
    assert "notes_ideas.pkl" in completions
    assert "contacts_autosave_1.pkl" not in completions
    assert "contacts_backup.pkl" not in completions
