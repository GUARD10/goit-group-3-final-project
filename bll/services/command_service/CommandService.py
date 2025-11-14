from typing import Optional

import inspect

from bll.decorators.CommandHandlerDecorator import command_handler_decorator
from bll.services.command_service.ICommandService import ICommandService
from bll.services.input_service.IInputService import IInputService
from bll.services.note_service.INoteService import INoteService
from bll.services.record_service.IRecordService import IRecordService
from dal.entities.Command import Command
from dal.entities.Record import Record
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from bll.registries.IRegistry import IRegistry


class CommandService(ICommandService):
    def __init__(
        self,
        record_service: IRecordService,
        note_service: INoteService,
        input_service: IInputService,
        file_service_registry: IRegistry,
    ) -> None:
        self.record_service = record_service
        self.note_service = note_service
        self.input_service = input_service
        self.file_service_registry = file_service_registry
        self._help_text: str | None = None

        self.commands: dict[str, Command] = {
            "hello": Command("hello", self.hello, "Greet the bot"),
            "add-contact": Command(
                "add-contact",
                self.add_contact,
                "Add a new contact: add-contact [name] [phone]",
            ),
            "add-phone": Command(
                "add-phone",
                self.add_phone,
                "Add new phone to contact: add-phone [name] [new_phone].",
            ),
            "show-phone": Command(
                "show-phone",
                self.show_phone,
                "Show a contact's phone by name: show-phone [name]",
            ),
            "show-all-contacts": Command(
                "show-all-contacts", self.show_all, "Show all contacts"
            ),
            "help": Command("help", self.help_command, "Show this help message"),
            "exit": Command("exit", self.exit_bot, "Exit the program"),
            "close": Command("close", self.exit_bot, "Close the program"),
            "add-birthday": Command(
                "add-birthday",
                self.add_birthday,
                "Add birthday to contact: add-birthday [name] [birthday]. "
                "Note it will replace birthday if exist",
            ),
            "show-birthday": Command(
                "show-birthday",
                self.show_birthday,
                "Show birthday to contact: show-birthday [name]",
            ),
            "upcoming-birthdays": Command(
                "upcoming-birthdays",
                self.birthdays,
                "Show upcoming birthdays for next N days (default 7): upcoming-birthdays [days]",
            ),
            "delete-contact": Command(
                "delete-contact",
                self.delete_contact,
                "Delete a contact: delete-contact [name]",
            ),
            "save-contact": Command(
                "save-contact",
                self.save_contact_state,
                'Save current state to file: save [name] or "save" without name for autosave',
            ),
            "load-contact": Command(
                "load-contact",
                self.load_contact_state,
                "Load state from file: load [name]",
            ),
            "delete-file": Command(
                "delete-file",
                self.delete_contact_file,
                "Delete the data file: delete-file [name]",
            ),
            "show-all-files": Command(
                "show-all-files", self.show_contact_files, "Show all data files"
            ),
            "search-contacts": Command(
                "search-contacts",
                self.search_contacts,
                "Search contacts by any field: search-contacts [text]",
            ),
            "add-note": Command(
                "add-note",
                self.add_note,
                "Add a new note: add-note [name]",
            ),
            "edit-note-title": Command(
                "edit-note-title",
                self.edit_note_title,
                "Edit note title: edit-note-title [name]",
            ),
            "edit-note-content": Command(
                "edit-note-content",
                self.edit_note_content,
                "Edit note content: edit-note-content [name]",
            ),
            "delete-note": Command(
                "delete-note",
                self.delete_note,
                "Delete a note: delete-note [name]",
            ),
            "show-all-notes": Command(
                "show-all-notes", self.show_all_notes, "Show all notes"
            ),
            "save-note": Command(
                "save-note",
                self.save_note_state,
                'Save current notes state to file: save-note [name] or "save-note" without name for autosave',
            ),
            "load-note": Command(
                "load-note",
                self.load_note_state,
                "Load notes state from file: load-note [name]",
            ),
            "delete-note-file": Command(
                "delete-note-file",
                self.delete_note_file,
                "Delete the notes data file: delete-note-file [name]",
            ),
            "show-all-note-files": Command(
                "show-all-note-files", self.show_note_files, "Show all notes data files"
            ),
        }

    def execute(self, command_name: str, arguments: list[str]) -> str:
        command = self.get_command(command_name)
        if not command:
            raise InvalidException("Invalid command")

        handler = command.handler
        sig = inspect.signature(handler)
        param_count = len(sig.parameters)

        return handler() if param_count == 0 else handler(arguments)

    def get_command(self, command: str) -> Optional[Command]:
        return self.commands.get(command)

    @command_handler_decorator
    def add_contact(self, arguments: list[str]) -> str:
        name, phone = [arg.strip() for arg in arguments]
        new_contact = Record(name, phone)
        self.record_service.save(new_contact)
        return f"Contact added. {new_contact}"

    @command_handler_decorator
    def add_phone(self, arguments: list[str]) -> str:
        name, new_phone = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name).update().add_phone(new_phone).build()
        )
        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

    @command_handler_decorator
    def show_phone(self, arguments: list[str]) -> str:
        name = arguments[0]
        contact = self.record_service.get_by_name(name)
        return ", ".join(p.value for p in contact.phones)

    @command_handler_decorator
    def delete_contact(self, arguments: list[str]) -> str:
        name = arguments[0]
        self.record_service.delete(name)
        return f"Contact '{name}' deleted."

    @command_handler_decorator
    def show_all(self) -> str:
        contacts = self.record_service.get_all()
        if not contacts:
            return "No contacts found."
        return "\n".join([f"{contact}" for contact in contacts])

    @command_handler_decorator
    def add_birthday(self, arguments: list[str]) -> str:
        name, birthday = arguments
        updated_contact = (
            self.record_service.get_by_name(name)
            .update()
            .set_birthday(birthday)
            .build()
        )
        self.record_service.update(name, updated_contact)
        return f"Contact updated. {name}"

    @command_handler_decorator
    def show_birthday(self, arguments: list[str]) -> str:
        name = arguments[0]
        contact = self.record_service.get_by_name(name)
        return f"Contact birthday: {contact.birthday}"

    @command_handler_decorator
    def birthdays(self, arguments: list[str] | None = None) -> str:
        days = 7
        if arguments:
            try:
                days = int(arguments[0])
                if days <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise InvalidException("Days must be a positive integer")

        contacts_with_upcoming_birthdays = (
            self.record_service.get_with_upcoming_birthdays(days)
        )

        if not contacts_with_upcoming_birthdays:
            return f"No birthdays in the next {days} days 🎂"

        return "\n".join(
            f"Contact: {contact.name} - {contact.birthday}"
            for contact in contacts_with_upcoming_birthdays
        )

    @command_handler_decorator
    def hello(self) -> str:
        return "How can I help you?"

    @command_handler_decorator
    def help_command(self) -> str:
        if not self._help_text:
            sections = {
                "Contacts": [
                    "add-contact",
                    "add-phone",
                    "show-phone",
                    "delete-contact",
                    "show-all-contacts",
                    "search-contacts",
                ],
                "Birthdays": ["add-birthday", "show-birthday", "upcoming-birthdays"],
                "Files": ["save", "load", "delete-file", "show-all-files"],
                "System": ["hello", "help", "exit", "close"],
                "Notes": [
                    "add-note",
                    "edit-note-title",
                    "edit-note-content",
                    "delete-note",
                    "show-all-notes",
                ],
            }
            lines: list[str] = []
            for title, cmds in sections.items():
                lines.append(f"\n{title}")
                for cmd in cmds:
                    if cmd in self.commands:
                        c = self.commands[cmd]
                        lines.append(f" - {c.name}: {c.description}")
            self._help_text = "Available commands:\n" + "\n".join(lines)
        return self._help_text

    @command_handler_decorator
    def exit_bot(self) -> None:
        self._save_all_states()

        raise ExitBotException("\nGood bye!")

    @command_handler_decorator
    def save_contact_state(self, arguments: list[str]) -> str:
        return self._save_state(arguments, "contacts")

    @command_handler_decorator
    def load_contact_state(self, arguments: list[str]) -> str:
        return self._load_state(arguments, "contacts")

    @command_handler_decorator
    def save_note_state(self, arguments: list[str]) -> str:
        return self._save_state(arguments, "notes")

    @command_handler_decorator
    def load_note_state(self, arguments: list[str]) -> str:
        return self._load_state(arguments, "notes")

    @command_handler_decorator
    def delete_contact_file(self, arguments: list[str]) -> str:
        return self._delete_state(arguments, "contacts")

    @command_handler_decorator
    def delete_note_file(self, arguments: list[str]) -> str:
        return self._delete_state(arguments, "notes")

    @command_handler_decorator
    def show_contact_files(self) -> str:
        return self._show_all_state_files("contacts")

    @command_handler_decorator
    def show_note_files(self) -> str:
        return self._show_all_state_files("notes")

    @command_handler_decorator
    def add_note(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()

        note_title = self.input_service.read_value(
            "\nEnter note title (or /cancel to abort)",
            allow_empty=False,
        )
        if note_title is None:
            return "Note creation cancelled."

        note_content = self.input_service.read_multiline(
            header=(
                "\nEnter note content (multi-line):\n"
                "- Type your text, multiple lines allowed\n"
                "- End input with an empty line\n"
                "- Minimum required length: 10 characters\n"
                "- Type /cancel to abort\n"
            ),
            min_len=10,
        )
        if note_content is None:
            return "Note creation cancelled."

        new_note = self.note_service.add(note_name, note_title, note_content)

        return f"Note added successfully.\n{new_note}"

    @command_handler_decorator
    def edit_note_title(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        note = self.note_service.get_by_name(note_name)

        new_title = self.input_service.read_value(
            "\nEdit title (/cancel to abort)",
            default=note.title.value,
            allow_empty=False,
        )
        if new_title is None:
            return "Editing cancelled."

        updated_note = note.update().set_title(new_title).build()
        self.note_service.update(note_name, updated_note)

        return f"Note title updated. New title: {updated_note.title}"

    @command_handler_decorator
    def edit_note_content(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        note = self.note_service.get_by_name(note_name)

        new_content = self.input_service.read_multiline(
            header=(
                "\nEnter new content (multi-line):\n"
                "- Existing content shown above\n"
                "- Type your new content below\n"
                "- Finish with an empty line\n"
                "- Type /cancel to abort\n"
            ),
            min_len=10,
            show_existing=note.content.value,
        )
        if new_content is None:
            return "Editing cancelled."

        updated_note = note.update().set_content(new_content).build()
        self.note_service.update(note_name, updated_note)

        return "Note content updated successfully."

    @command_handler_decorator
    def delete_note(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        self.note_service.delete(note_name)
        return f"Note '{note_name}' deleted."

    @command_handler_decorator
    def show_all_notes(self) -> str:
        notes = self.note_service.get_all()
        if not notes:
            return "No notes found."
        return "\n".join([f"{note}" for note in notes])

    @command_handler_decorator
    def search_contacts(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.record_service.search(query)

        if not matches:
            return "No matching contacts found."

        return "\n".join([f"{contact}" for contact in matches])

    def _save_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)

        try:
            file_name = arguments[0]
        except IndexError:
            file_name = "autosave"

        file_service.save_with_name(file_name)
        return f"{key} state saved to file '{file_name}'."

    def _load_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)

        file_name = arguments[0]
        file_service.load_by_name(file_name)

        return f"{key} state loaded from file '{file_name}'."

    def _delete_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)
        file_name = arguments[0]
        file_service.delete_by_name(file_name)
        return f"File '{file_name}' deleted."

    def _show_all_state_files(self, key: str) -> str:
        file_service = self.file_service_registry.get(key)
        file_names = file_service.get_file_list()

        if not file_names:
            return "No files found."

        return "Available files:\n" + "\n".join(file_names)

    def _save_all_states(self) -> None:
        for key, service in self.file_service_registry.get_all().items():
            if service.is_save_able():
                saved_file = service.save_with_name()
                print(f"[{key}] state saved to {saved_file}")
