from prompt_toolkit.document import Document
from bll.helpers.PromptCompleter import PromptCompleter


class FakeCommand:
    def __init__(self, name: str):
        self.name = name
        self.handler = None
        self.description = ""


class FakeCommandService:
    def __init__(self):
        # Команди, які нас цікавлять для автокомпліта
        names = [
            "show-phone",
            "add-phone",
            "add-email",
            "update-email",
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
    def __init__(self, title: str):
        # емулюємо note.title.value
        self.title = type("T", (), {"value": title})


class FakeNoteService:
    def __init__(self):
        self._notes = [
            FakeNote("Shopping list"),
            FakeNote("Work tasks"),
            FakeNote("Roman study plan"),
        ]

    def get_all(self):
        return self._notes


def collect_completions(completer: PromptCompleter, text: str) -> list[str]:
    """
    Допоміжна функція: створює Document і повертає список текстів completion’ів.
    """
    doc = Document(text=text, cursor_position=len(text))
    return [c.text for c in completer.get_completions(doc, None)]


def test_command_name_completion_by_prefix():
    """
    Перевіряємо, що при введенні префіксу першого слова
    (команди) PromptCompleter підказує відповідні команди.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише "add-" → очікуємо, що будуть "add-phone", "add-email"
    completions = collect_completions(completer, "add-")

    assert "add-phone" in completions
    assert "add-email" in completions
    # але, наприклад, "edit-note-title" не має бути в цих підказках
    assert "edit-note-title" not in completions


def test_contact_commands_suggest_contact_names():
    """
    Для contact_commands (наприклад show-phone) друге слово має доповнюватися
    іменами контактів з RecordService.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише: "show-phone Ro"
    completions = collect_completions(completer, "show-phone Ro")

    # Очікуємо, що підкаже "Roman"
    assert "Roman" in completions
    # А, наприклад, "John" не підходить під префікс "Ro"
    assert "John" not in completions


def test_note_title_commands_suggest_note_titles():
    """
    Для note_title_commands (edit-note-title, edit-note-content, delete-note)
    другий аргумент має доповнюватися назвами нотаток.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише: "edit-note-title Ro"
    completions = collect_completions(completer, "edit-note-title Ro")

    # Має запропонувати заголовок "Roman study plan"
    assert "Roman study plan" in completions

    # А, наприклад, "Shopping list" не підходить під префікс "Ro"
    assert "Shopping list" not in completions
