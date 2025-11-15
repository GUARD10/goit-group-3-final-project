from typing import Iterable

from prompt_toolkit.completion import Completer, Completion

from bll.services.command_service.CommandService import CommandService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService


class PromptCompleter(Completer):
    def __init__(
        self,
        command_service: CommandService,
        record_service: RecordService,
        note_service: NoteService,
    ):
        self._command_service = command_service
        self._record_service = record_service
        self._note_service = note_service

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        parts = text.split()

        # Нічого не введено → пропонуємо всі команди
        if len(parts) == 0:
            for name in self._command_service.commands.keys():
                yield Completion(name, start_position=0)
            return

        # Доповнення імені команди (перше слово)
        if len(parts) == 1 and not text.endswith(" "):
            prefix = parts[0]
            for name in self._command_service.commands.keys():
                if name.startswith(prefix):
                    yield Completion(name, start_position=-len(prefix))
            return

        cmd = parts[0]

        # # Якщо це тег (слово, що починається з "#") — підказуємо теги
        # last_token = parts[-1]
        # if last_token.startswith("#"):
        #     tag_prefix = last_token[1:]  # без '#'

        #     # збираємо всі теги з нотаток
        #     all_tags: set[str] = set()
        #     for note in self._note_service.get_all():
        #         # припускаю, що note.tags — ітерований список/сет Tag
        #         tags = getattr(note, "tags", []) or []
        #         for tag in tags:
        #             tag_value = getattr(tag, "value", str(tag))
        #             all_tags.add(tag_value)

        #     for tag in sorted(all_tags):
        #         if tag.startswith(tag_prefix):
        #             # підставляємо всю штуку разом з '#'
        #             yield Completion("#" + tag, start_position=-len(last_token))
        #     return

        # Основні команди: підказуємо імена контактів 
        contact_commands = {
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
        }

        if cmd in contact_commands:
            # перший аргумент після команди — ім'я контакту
            if len(parts) == 2 and not text.endswith(" "):
                prefix = parts[1]
                for rec in self._record_service.get_all():
                    name = rec.name.value
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            return

        # Команди для нотаток: підказуємо назви нотаток
        note_title_commands = {
            "edit-note-title",
            "edit-note-content",
            "delete-note",
        }

        if cmd in note_title_commands:
            # перший аргумент — назва нотатки
            if len(parts) == 2 and not text.endswith(" "):
                prefix = parts[1]
                for note in self._note_service.get_all():
                    # припускаю, що note.title.value
                    title = getattr(note.title, "value", str(note.title))
                    if title.startswith(prefix):
                        yield Completion(title, start_position=-len(prefix))
            return

        # Для інших команд поки не доповнюємо нічого
        return
