from typing import Iterable, List

from prompt_toolkit.completion import Completer, Completion

from bll.services.command_service.command_service import CommandService
from bll.services.note_service.note_service import NoteService
from bll.services.record_service.record_service import RecordService


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

    def _get_contact_names(self) -> List[str]:
        names = []
        for rec in self._record_service.get_all():
            name = getattr(getattr(rec, "name", None), "value", None)
            if name:
                names.append(str(name))
        return sorted(set(names))

    def _get_record_by_name(self, name: str):
        for rec in self._record_service.get_all():
            rec_name = getattr(getattr(rec, "name", None), "value", None)
            if rec_name == name:
                return rec
        return None

    def _get_contact_emails(self, contact_name: str) -> List[str]:
        rec = self._get_record_by_name(contact_name)
        if not rec:
            return []

        emails = []
        # варіант 1: список емейлів
        if hasattr(rec, "emails"):
            for e in getattr(rec, "emails", []):
                value = getattr(e, "value", str(e))
                if value:
                    emails.append(str(value))
        # варіант 2: один емейл
        elif hasattr(rec, "email"):
            value = getattr(rec.email, "value", str(rec.email))
            if value:
                emails.append(str(value))

        return sorted(set(emails))

    def _get_note_names(self) -> List[str]:
        names = []
        for note in self._note_service.get_all():
            name = getattr(getattr(note, "name", None), "value", None)
            if name:
                names.append(str(name))
        return sorted(set(names))

    def _get_contact_files(self) -> List[str]:
        if hasattr(self._record_service, "list_contact_files"):
            files = self._record_service.list_contact_files()
        elif hasattr(self._record_service, "get_contact_files"):
            files = self._record_service.get_contact_files()
        else:
            files = []
        return sorted(str(f) for f in files)

    def _get_note_files(self) -> List[str]:
        if hasattr(self._note_service, "list_note_files"):
            files = self._note_service.list_note_files()
        elif hasattr(self._note_service, "get_note_files"):
            files = self._note_service.get_note_files()
        else:
            files = []
        return sorted(str(f) for f in files)

    def _get_all_tags(self) -> list[str]:
        tags: set[str] = set()
        for note in self._note_service.get_all():
            raw_tags = getattr(note, "tags", []) or []
            for tag in raw_tags:
                tag_value = getattr(tag, "value", str(tag))
                if tag_value:
                    tags.add(str(tag_value))
        return sorted(tags)

    def _get_tags_for_note(self, note_name: str) -> list[str]:
        for note in self._note_service.get_all():
            n = getattr(getattr(note, "name", None), "value", None)
            if n == note_name:
                raw_tags = getattr(note, "tags", []) or []
                tags = []
                for tag in raw_tags:
                    tag_value = getattr(tag, "value", str(tag))
                    if tag_value:
                        tags.append(str(tag_value))
                return sorted(set(tags))
        return []

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        parts = text.split()

        # 1. Нічого не введено - всі команди
        if len(parts) == 0:
            for name in self._command_service.commands.keys():
                yield Completion(name, start_position=0)
            return

        # 2. Доповнення імені команди (перше слово)
        if len(parts) == 1 and not text.endswith(" "):
            prefix = parts[0]
            for name in self._command_service.commands.keys():
                if name.startswith(prefix):
                    yield Completion(name, start_position=-len(prefix))
            return

        # Далі працюємо тільки з аргументами (команда вже є)
        cmd = parts[0]

        # Визначаємо, який саме аргумент зараз доповнюємо
        if text.endswith(" "):
            # курсор після пробілу - починаємо НОВИЙ аргумент
            arg_index = len(parts)  # 0 - команда, 1 - перший аргумент і т.д.
            prefix = ""
        else:
            # курсор всередині останнього токена
            arg_index = len(parts) - 1
            prefix = parts[-1]

        # =========================================================
        #        КОМАНДИ ДЛЯ КОНТАКТІВ
        # =========================================================

        # add-contact [name] [phone] - тільки назва команди, аргументи не доповнюємо
        if cmd == "add-contact":
            return

        # add-phone [name] [phone]
        # - якщо контакт існує, підказуємо ім'я (1-й аргумент)
        if cmd == "add-phone":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            # phone не доповнюємо
            return

        # show-phone [name] - підказуємо існуючі імена
        if cmd == "show-phone":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            return

        # add-email [name] [new_email] - тільки ім'я
        if cmd == "add-email":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            # new_email не доповнюємо
            return

        # update-email [name] [old_email] [new_email]
        # - 1-й аргумент - ім'я
        # - 2-й аргумент - існуючий емейл контактa
        if cmd == "update-email":
            if arg_index == 1:
                # ім'я контакту
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            elif arg_index == 2:
                # old_email
                contact_name = parts[1]
                for email in self._get_contact_emails(contact_name):
                    if email.startswith(prefix):
                        yield Completion(email, start_position=-len(prefix))
            # new_email не доповнюємо
            return

        # delete-email [name] [email]
        # - 1-й аргумент - ім'я
        # - 2-й аргумент - емейл цього контакту
        if cmd == "delete-email":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            elif arg_index == 2:
                contact_name = parts[1]
                for email in self._get_contact_emails(contact_name):
                    if email.startswith(prefix):
                        yield Completion(email, start_position=-len(prefix))
            return

        # set-address [name] [address] - тільки ім'я
        if cmd == "set-address":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            # address не доповнюємо
            return

        # delete-address [name] - ім'я
        if cmd == "delete-address":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            return

        # delete-contact [name] → ім'я
        if cmd == "delete-contact":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            return

        # show-all-contacts - нічого не доповнюємо
        if cmd == "show-all-contacts":
            return

        # search-contacts [text] - нічого не доповнюємо
        if cmd == "search-contacts":
            return

        # add-birthday [name] [birthday] - тільки ім'я
        if cmd == "add-birthday":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            # birthday не доповнюємо
            return

        # show-birthday [name] - ім'я
        if cmd == "show-birthday":
            if arg_index == 1:
                for name in self._get_contact_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))
            return

        # upcoming-birthdays [days] - нічого не доповнюємо
        if cmd == "upcoming-birthdays":
            return

        # calendar [month] [year] - нічого не доповнюємо
        if cmd == "calendar":
            return

        # save-contact [name] - нічого не доповнюємо (тільки сама команда)
        if cmd == "save-contact":
            return

        # load-contact [name] - підказуємо імена файлів
        if cmd == "load-contact":
            if arg_index == 1:
                for fname in self._get_contact_files():
                    if fname.startswith(prefix):
                        yield Completion(fname, start_position=-len(prefix))
            return

        # delete-contact-file [name] → підказуємо імена файлів
        if cmd == "delete-contact-file":
            if arg_index == 1:
                for fname in self._get_contact_files():
                    if fname.startswith(prefix):
                        yield Completion(fname, start_position=-len(prefix))
            return

        # contacts-files - тільки команда, 2-й параметр не доповнюємо
        if cmd == "contacts-files":
            return

        # =========================================================
        #        КОМАНДИ ДЛЯ НОТАТОК
        # =========================================================

        # add-note [name] - тільки команда, ім'я не підказуємо (створення)
        if cmd == "add-note":
            return

        # Команди, де 1-й аргумент — назва існуючої нотатки
        note_title_commands = {
            "edit-note-title",
            "edit-note-content",
            "delete-note",
            "add-note-tags",
            "remove-note-tag",
        }

        if cmd in note_title_commands:
            # Перший аргумент: ім'я нотатки
            if arg_index == 1:
                for name in self._get_note_names():
                    if name.startswith(prefix):
                        yield Completion(name, start_position=-len(prefix))

            # =========================================================
            #        АВТОКОМПЛІТ ДЛЯ ТЕГІВ
            # =========================================================

            # add-note-tags [name] [tag]
            if cmd == "add-note-tags" and arg_index >= 2:
                for tag in self._get_all_tags():
                    if tag.startswith(prefix):
                        yield Completion(tag, start_position=-len(prefix))

            # remove-note-tag [name] [tag]
            if cmd == "remove-note-tag" and arg_index == 2:
                note_name = parts[1]
                for tag in self._get_tags_for_note(note_name):
                    if tag.startswith(prefix):
                        yield Completion(tag, start_position=-len(prefix))

            return

        # show-all-notes - нічого
        if cmd == "show-all-notes":
            return

        # search-notes [text] - нічого
        if cmd == "search-notes":
            return

        # show-notes-by-tag [tag]
        if cmd == "show-notes-by-tag":
            if arg_index == 1:
                for tag in self._get_all_tags():
                    if tag.startswith(prefix):
                        yield Completion(tag, start_position=-len(prefix))
            return

        # save-note [name] - тільки команда
        if cmd == "save-note":
            return

        # load-note [name] - імена файлів
        if cmd == "load-note":
            if arg_index == 1:
                for fname in self._get_note_files():
                    if fname.startswith(prefix):
                        yield Completion(fname, start_position=-len(prefix))
            return

        # delete-note-file [name] - імена файлів
        if cmd == "delete-note-file":
            if arg_index == 1:
                for fname in self._get_note_files():
                    if fname.startswith(prefix):
                        yield Completion(fname, start_position=-len(prefix))
            return

        # note-files - тільки команда
        if cmd == "note-files":
            return

        # =========================================================
        #        SYSTEM-КОМАНДИ
        # =========================================================
        # hello, help, exit, close - без аргументів, нічого не підказуємо
        if cmd in {"hello", "help", "exit", "close"}:
            return

        # Для інших команд поки не доповнюємо нічого
        return
