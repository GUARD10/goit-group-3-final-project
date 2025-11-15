from prompt_toolkit.document import Document

from bll.helpers.prompt_completer import PromptCompleter


class FakeCommand:
    def __init__(self, name: str):
        self.name = name
        self.handler = None
        self.description = ""


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
            "help",
            "exit",
        ]

        self.commands = {name: FakeCommand(name) for name in names}


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


def test_command_name_completion_by_prefix():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "add-")

    assert "add-phone" in completions
    assert "add-email" in completions
    assert "edit-note-title" not in completions


def test_contact_commands_suggest_contact_names():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "add-phone Ro")

    assert "Roman" in completions
    assert "John" not in completions


def test_note_title_commands_suggest_note_names():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "edit-note-title Ro")

    assert "Roman study plan" in completions

    assert "Shopping list" not in completions


def test_add_note_tags_suggests_all_tags_by_prefix():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "add-note-tags Roman study plan t")

    assert "todo" in completions
    assert "urgent" not in completions


def test_remove_note_tag_suggests_tags_for_specific_note():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "remove-note-tag Roman t")

    assert "todo" in completions
    assert "roman-tag" not in completions


def test_show_notes_by_tag_suggests_all_tags():
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    completions = collect_completions(completer, "show-notes-by-tag t")

    assert "todo" in completions
    assert "work" not in completions
