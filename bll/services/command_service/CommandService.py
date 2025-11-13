from typing import Optional

import inspect

from bll.decorators.CommandHandlerDecorator import command_handler_decorator
from bll.services.command_service.ICommandService import ICommandService
from bll.services.input_service.IInputService import IInputService
from bll.services.note_service.INoteService import INoteService
from bll.services.pickle_file_service.IPickleFileService import IPickleFileService
from bll.services.record_service.IRecordService import IRecordService
from bll.helpers.TagPalette import TAG_COLORS
from dal.entities.Command import Command
from dal.entities.Record import Record
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException


class CommandService(ICommandService):
    TAG_COLOR_CHOICES = TAG_COLORS

    def __init__(
        self,
        record_service: IRecordService,
        file_service: IPickleFileService,
        note_service: INoteService,
        input_service: IInputService,
    ) -> None:
        self.record_service = record_service
        self.file_service = file_service
        self.note_service = note_service
        self.input_service = input_service
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
            "save": Command(
                "save",
                self.save_state,
                'Save current state to file: save [name] or "save" without name for autosave',
            ),
            "load": Command(
                "load", self.load_state, "Load state from file: load [name]"
            ),
            "delete-file": Command(
                "delete-file",
                self.delete_file,
                "Delete the data file: delete-file [name]",
            ),
            "show-all-files": Command(
                "show-all-files", self.show_all_files, "Show all data files"
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
            "search-notes": Command(
                "search-notes",
                self.search_notes,
                "Search notes by any field: search-notes [text]",
            ),
            "add-note-tags": Command(
                "add-note-tags",
                self.add_note_tags,
                "Attach tags to a note: add-note-tags [name] [tag[:color] ...]",
            ),
            "remove-note-tag": Command(
                "remove-note-tag",
                self.remove_note_tag,
                "Remove tag from a note: remove-note-tag [name] [tag]",
            ),
            "show-notes-by-tag": Command(
                "show-notes-by-tag",
                self.show_notes_by_tag,
                "Show notes filtered/sorted by tag: show-notes-by-tag [tag]",
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
                    "search-notes",
                    "add-note-tags",
                    "remove-note-tag",
                    "show-notes-by-tag",
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
        if self.file_service.is_save_able():
            saved_file_name = self.file_service.save_with_name()
            print(f"State saved to {saved_file_name}")
        raise ExitBotException("\nGood bye!")

    @command_handler_decorator
    def save_state(self, arguments: list[str]) -> str:
        try:
            file_name = arguments[0]
        except IndexError:
            file_name = "autosave"

        self.file_service.save_with_name(file_name)
        return f"State saved to file '{file_name}'."

    @command_handler_decorator
    def load_state(self, arguments: list[str]) -> str:
        file_name = arguments[0]
        self.file_service.load_by_name(file_name)
        return f"State loaded from file '{file_name}'."

    @command_handler_decorator
    def delete_file(self, arguments: list[str]) -> str:
        file_name = arguments[0]
        self.file_service.delete_by_name(file_name)
        return f"File '{file_name}' deleted."

    @command_handler_decorator
    def show_all_files(self) -> str:
        file_names = self.file_service.get_file_list()
        return "Available files:\n" + "\n".join(file_names)

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

        tags = self._collect_tags_interactively()

        new_note = self.note_service.add(
            note_name,
            note_title,
            note_content,
            **({"tags": tags} if "tags" in inspect.signature(self.note_service.add).parameters else {})
        )

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
        notes = self.note_service.get_all_sorted_by_tags()
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

    @command_handler_decorator
    def search_notes(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.note_service.search(query)

        if not matches:
            return "No matching notes found."

        return "\n".join([f"{note}" for note in matches])

    def _collect_tags_interactively(self) -> list[tuple[str, str | None]]:
        tags: list[tuple[str, str | None]] = []

        existing_tags = self.note_service.get_distinct_tags()
        if existing_tags:
            choices = [
                (
                    tag.value,
                    f"{tag.value}" + (f" ({tag.color})" if tag.color else ""),
                )
                for tag in existing_tags
            ]
            selected = self.input_service.choose_multiple_from_list(
                "Existing Tags",
                "Select tags to add (use arrows + space, Enter to confirm, Esc to skip)",
                choices,
            ) or []

            color_map = {tag.value: tag.color for tag in existing_tags}
            for tag_name in selected:
                tags.append((tag_name, color_map.get(tag_name)))

        while True:
            raw = self.input_service.read_value(
                "\nEnter new tags (comma-separated, use name or name:#hex, blank to finish)",
                allow_empty=True,
            )

            if not raw:
                break

            entries = [entry.strip() for entry in raw.split(",") if entry.strip()]
            if not entries:
                break

            for entry in entries:
                if ":" in entry:
                    name, raw_color = entry.split(":", 1)
                    color_value: str | None = raw_color.strip() or None
                    tags.append((name.strip(), color_value))
                else:
                    color_value = self._prompt_tag_color(entry)
                    tags.append((entry, color_value))

        return tags

    def _parse_tag_specs(self, specs: list[str]) -> list[tuple[str, str | None]]:
        parsed: list[tuple[str, str | None]] = []
        for spec in specs:
            if ":" in spec:
                name, color = spec.split(":", 1)
            else:
                name, color = spec, None

            name = name.strip()
            if not name:
                continue
            color = color.strip() if color else None
            parsed.append((name, color))

        return parsed

    def _prompt_tag_color(self, tag_name: str) -> str | None:
        options = [("__auto__", "Auto assign color")]
        options.extend(
            [
                (code, f"{label} ({code})")
                for label, code in self.TAG_COLOR_CHOICES
            ]
        )
        options.append(("__custom__", "Custom color..."))

        choice = self.input_service.choose_from_list(
            f"Tag color for '{tag_name}'",
            "Use arrows to choose and Enter to confirm.",
            options,
        )

        if choice is None:
            manual = self.input_service.read_value(
                "Enter custom color (e.g. #FF00AA) or leave empty for auto",
                allow_empty=True,
            )
            return manual or None

        if choice == "__auto__":
            return None

        if choice == "__custom__":
            return self.input_service.read_value(
                "Enter custom color (e.g. #FF00AA or teal)", allow_empty=False
            )

        return choice

    @command_handler_decorator
    def add_note_tags(self, arguments: list[str]) -> str:
        if not arguments:
            raise InvalidException(
                "Usage: add-note-tags [note-name] [tag[:color] ...]"
            )

        note_name = arguments[0].strip()
        tag_specs = arguments[1:]
        tags = self._parse_tag_specs(tag_specs)

        if not tags:
            tags = self._collect_tags_interactively()

        if not tags:
            raise InvalidException("At least one tag is required")

        updated_note = self.note_service.add_tags(note_name, tags)

        return (
            f"Tags updated. Current tags: {', '.join(updated_note.tag_names())}"
        )

    @command_handler_decorator
    def remove_note_tag(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            raise InvalidException(
                "Usage: remove-note-tag [note-name] [tag-name]"
            )

        note_name = arguments[0].strip()
        tag_name = arguments[1].strip()
        self.note_service.remove_tag(note_name, tag_name)

        return f"Tag '{tag_name}' removed from note '{note_name}'."

    @command_handler_decorator
    def show_notes_by_tag(self, arguments: list[str]) -> str:
        tag_name = arguments[0].strip() if arguments else None
        if tag_name == "":
            tag_name = None
        notes = self.note_service.get_all_sorted_by_tags(tag_name)

        if not notes:
            if tag_name:
                return f"No notes found with tag '{tag_name}'."
            return "No notes found."

        heading = (
            f"Notes with tag '{tag_name}':" if tag_name else "Notes sorted by tags:"
        )
        rendered = "\n".join([f"{note}" for note in notes])
        return f"{heading}\n{rendered}"
