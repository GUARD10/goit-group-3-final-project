from prompt_toolkit.document import Document

from bll.helpers.prompt_completer import PromptCompleter


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
            "add-note-tags",
            "remove-note-tag",
            "show-notes-by-tag",  # додали, бо є логіка для тегів
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
            # окрема нота з простим name без пробілів, щоб зручно тестувати remove-note-tag
            FakeNote("Roman", tags=["roman-tag", "todo"]),
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


def test_note_title_commands_suggest_note_names():
    """
    Для note_title_commands (edit-note-title, edit-note-content, delete-note,
    add-note-tags, remove-note-tag)
    перший аргумент має доповнюватися іменами нотаток (name), а не title.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише: "edit-note-title Ro"
    completions = collect_completions(completer, "edit-note-title Ro")

    # Має запропонувати ім'я нотатки, яке починається на "Ro"
    # (FakeNoteService повертає нотатку з name = "Roman study plan")
    assert "Roman study plan" in completions

    # А, наприклад, "Shopping list" не підходить під префікс "Ro"
    assert "Shopping list" not in completions


def test_add_note_tags_suggests_all_tags_by_prefix():
    """
    Для add-note-tags [name] [tag] другий та наступні аргументи
    мають доповнюватися всіма відомими тегами по префіксу.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише: "add-note-tags Roman study plan t"
    # parts = ["add-note-tags", "Roman", "study", "plan", "t"]
    completions = collect_completions(completer, "add-note-tags Roman study plan t")

    # У всіх нотатках є теги: groceries, todo, work, urgent, study, roman-tag
    # За префіксом "t" очікуємо "todo"
    assert "todo" in completions
    # А, наприклад, "urgent" не має з'являтися, бо не починається на "t"
    assert "urgent" not in completions


def test_remove_note_tag_suggests_tags_for_specific_note():
    """
    Для remove-note-tag [name] [tag] теги мають підказуватися
    тільки з обраної нотатки.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Використаємо нотатку з простим name "Roman", щоб не ламатися на пробілах
    # parts = ["remove-note-tag", "Roman", "t"]
    completions = collect_completions(completer, "remove-note-tag Roman t")

    # У нотатки "Roman" теги: ["roman-tag", "todo"]
    # Префікс "t" → очікуємо "todo"
    assert "todo" in completions
    # "roman-tag" не підходить під префікс "t"
    assert "roman-tag" not in completions


def test_show_notes_by_tag_suggests_all_tags():
    """
    Для show-notes-by-tag [tag] автокомпліт має пропонувати список усіх тегів.
    """
    completer = PromptCompleter(
        command_service=FakeCommandService(),
        record_service=FakeRecordService(),
        note_service=FakeNoteService(),
    )

    # Користувач пише: "show-notes-by-tag t"
    completions = collect_completions(completer, "show-notes-by-tag t")

    # За префіксом "t" очікуємо тег "todo"
    assert "todo" in completions
    # Тег "work" не має підходити під префікс "t"
    assert "work" not in completions
