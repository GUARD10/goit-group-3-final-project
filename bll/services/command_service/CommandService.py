from typing import Optional

import inspect

from bll.decorators.CommandHandlerDecorator import command_handler_decorator
from bll.services.command_service.ICommandService import ICommandService
from bll.services.input_service.IInputService import IInputService
from bll.services.note_service.INoteService import INoteService
from bll.services.record_service.IRecordService import IRecordService
from bll.helpers.TagPalette import TAG_COLORS
from dal.entities.Command import Command
from dal.entities.Record import Record
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from bll.registries.IRegistry import IRegistry

from colorama import Fore as cf
from colorama import Style as cs


class CommandService(ICommandService):
    TAG_COLOR_CHOICES = TAG_COLORS

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
                "add-contact [name] [phone]",
                self.add_contact,
                "Add a new contact",
            ),
            "add-phone": Command(
                "add-phone [name] [new_phone]",
                self.add_phone,
                "Add new phone to contact.",
            ),
            "show-phone": Command(
                "show-phone [name]",
                self.show_phone,
                "Show a contact's phone by name",
            ),
            "add-email": Command(
                "add-email",
                self.add_email,
                "Add new Email to contact: add-email [name] [new_email].",
            ),
            "update-email": Command(
                "update-email",
                self.update_email,
                "Update Email for contact: update-email [name] [old_email] [new_email].",
            ),
            "delete-email": Command(
                "delete-email",
                self.delete_email,
                "Delete Email for contact: delete-email [name] [email].",
            ),
            "set-address": Command(
                "set-address",
                self.set_address,
                "Set address for contact: set-address [name] [address].",
            ),
            "delete-address": Command(
                "delete-address",
                self.delete_address,
                "Delete address for contact: delete-address [name].",
            ),
            "help": Command("help", self.help_command, "Show this help message"),
            "exit": Command("exit", self.exit_bot, "Exit the program"),
            "close": Command("close", self.exit_bot, "Close the program"),
            "add-birthday": Command(
                "add-birthday [name] [birthday]",
                self.add_birthday,
                "Add birthday to contact.Note it will replace birthday if exist",
            ),
            "show-birthday": Command(
                "show-birthday [name]",
                self.show_birthday,
                "Show birthday to contact",
            ),
            "upcoming-birthdays": Command(
                "upcoming-birthdays [days]",
                self.birthdays,
                "Show upcoming birthdays for next N days (default 7)",
            ),
            "delete-contact": Command(
                "delete-contact [name]",
                self.delete_contact,
                "Delete a contact",
            ),
            "save-contact": Command(
                "save-contact [name]?",
                self.save_contact_state,
                "Save current state to file. NOTE save without name for autosave",
            ),
            "load-contact": Command(
                "load-contact [name]",
                self.load_contact_state,
                "Load state from file",
            ),
            "delete-contact-file": Command(
                "delete-contact-file [name]",
                self.delete_contact_file,
                "Delete the data file",
            ),
            "contacts-files": Command(
                "contacts-files", self.show_contact_files, "Show all contact files"
            ),
            "search-contacts": Command(
                "search-contacts [text]",
                self.search_contacts,
                "Search contacts by any field",
            ),
            "add-note": Command(
                "add-note [name]",
                self.add_note,
                "Add a new note",
            ),
            "edit-note-title": Command(
                "edit-note-title [name]",
                self.edit_note_title,
                "Edit note title",
            ),
            "edit-note-content": Command(
                "edit-note-content [name]",
                self.edit_note_content,
                "Edit note content",
            ),
            "delete-note": Command(
                "delete-note [name]",
                self.delete_note,
                "Delete a note",
            ),
            "show-all-notes": Command(
                "show-all-notes", self.show_all_notes, "Show all notes"
            ),
            "search-notes": Command(
                "search-notes [text]",
                self.search_notes,
                "Search notes by any field",
            ),
            "add-note-tags": Command(
                "add-note-tags [name] [tag[:color] ...]",
                self.add_note_tags,
                "Attach tags to a note",
            ),
            "remove-note-tag": Command(
                "remove-note-tag [name] [tag]",
                self.remove_note_tag,
                "Remove tag from a note",
            ),
            "show-notes-by-tag": Command(
                "show-notes-by-tag [tag]",
                self.show_notes_by_tag,
                "Show notes filtered/sorted by tag",
            ),
            "save-note": Command(
                "save-note [name]?",
                self.save_note_state,
                "Save current notes state to file. NOTE save without name for autosave",
            ),
            "load-note": Command(
                "load-note [name]",
                self.load_note_state,
                "Load notes state from file",
            ),
            "delete-note-file": Command(
                "delete-note-file [name]",
                self.delete_note_file,
                "Delete the notes data file",
            ),
            "note-files": Command(
                "show-all-note-files", self.show_note_files, "Show all notes files"
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

        return f"{cf.GREEN}Contact added.{cs.RESET_ALL}{new_contact}"

    @command_handler_decorator
    def add_phone(self, arguments: list[str]) -> str:
        name, new_phone = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name).update().add_phone(new_phone).build()
        )
        self.record_service.update(name, contact)

        return f"{cf.GREEN}Contact updated.{cs.RESET_ALL}{contact}"

    @command_handler_decorator
    def show_phone(self, arguments: list[str]) -> str:
        name = arguments[0]
        contact = self.record_service.get_by_name(name)
        return ", ".join(p.value for p in contact.phones)

    @command_handler_decorator
    def delete_contact(self, arguments: list[str]) -> str:
        name = arguments[0]
        self.record_service.delete(name)
        return (
            f"{cf.GREEN}Contact '{cf.MAGENTA}{name}{cf.GREEN}' deleted.{cs.RESET_ALL}"
        )

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
        return f"{cf.GREEN}Contact updated. {cs.RESET_ALL}{name}"

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
    def add_email(self, arguments: list[str]) -> str:
        name, new_email = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name).update().add_email(new_email).build()
        )
        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

    @command_handler_decorator
    def update_email(self, arguments: list[str]) -> str:
        # очікуємо: name, old_email, new_email
        name, old_email, new_email = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name)
            .update()
            .update_email(old_email, new_email)
            .build()
        )

        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

    @command_handler_decorator
    def delete_email(self, arguments: list[str]) -> str:
        # очікуємо: name, email_to_delete
        name, email_to_delete = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name)
            .update()
            .remove_email(email_to_delete)
            .build()
        )

        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

    @command_handler_decorator
    def set_address(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            raise InvalidException("Usage: set-address [name] [address]")
        
        name = arguments[0].strip()
        address = " ".join(arg.strip() for arg in arguments[1:])

        contact = (
            self.record_service
            .get_by_name(name)
            .update()
            .set_address(address)
            .build()
        )
        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

    @command_handler_decorator
    def delete_address(self, arguments: list[str]) -> str:
        # очікуємо: тільки name
        (name,) = [arg.strip() for arg in arguments]

        contact = self.record_service.get_by_name(name).update().clear_address().build()
        self.record_service.update(name, contact)

        return f"Contact updated. {contact}"

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
                    "add-email",
                    "update-email",
                    "delete-email",
                    "set-address",
                    "delete-address",
                    "delete-contact",
                    "show-all-contacts",
                    "search-contacts",
                ],
                "Birthdays": ["add-birthday", "show-birthday", "upcoming-birthdays"],
                "Files": [
                    "save-contact",
                    "load-contact",
                    "delete-contact-file",
                    "contacts-files",
                    "save-note",
                    "load-note",
                    "delete-note-file",
                    "note-files",
                ],
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
                lines.append(f"\n{cf.BLUE}{title}{cs.RESET_ALL}")
                for cmd in cmds:
                    if cmd in self.commands:
                        c = self.commands[cmd]
                        lines.append(
                            f" - {cf.CYAN}{c.name}{cs.RESET_ALL}: {c.description}"
                        )
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
            return f"{cf.YELLOW}Note creation cancelled.{cs.RESET_ALL}"

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
            return f"{cf.YELLOW}Note creation cancelled.{cs.RESET_ALL}"

        tags = self._collect_tags_interactively()

        new_note = self.note_service.add(
            note_name,
            note_title,
            note_content,
            **(
                {"tags": tags}
                if "tags" in inspect.signature(self.note_service.add).parameters
                else {}
            ),
        )

        return f"{cf.GREEN}Note added successfully.{cs.RESET_ALL}\n{new_note}"

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
            return f"{cf.YELLOW}Editing cancelled.{cs.RESET_ALL}"

        updated_note = note.update().set_title(new_title).build()
        self.note_service.update(note_name, updated_note)

        return f"{cf.GREEN}Note title updated. New title: {cf.MAGENTA}{updated_note.title}{cs.RESET_ALL}"

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
            return f"{cf.YELLOW}Editing cancelled.{cs.RESET_ALL}"

        updated_note = note.update().set_content(new_content).build()
        self.note_service.update(note_name, updated_note)

        return f"{cf.GREEN}Note content updated successfully.{cs.RESET_ALL}"

    @command_handler_decorator
    def delete_note(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        self.note_service.delete(note_name)
        return f"{cf.GREEN}Note '{cf.MAGENTA}{note_name}' deleted.{cs.RESET_ALL}"

    @command_handler_decorator
    def show_all_notes(self) -> str:
        notes = self.note_service.get_all_sorted_by_tags()
        if not notes:
            return f"{cf.RED}No notes found.{cs.RESET_ALL}"
        return "\n".join([f"{note}" for note in notes])

    @command_handler_decorator
    def search_contacts(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.record_service.search(query)

        if not matches:
            return f"{cf.RED}No matching contacts found.{cs.RESET_ALL}"

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
            selected = (
                self.input_service.choose_multiple_from_list(
                    "Existing Tags",
                    "Select tags to add (use arrows + space, Enter to confirm, Esc to skip)",
                    choices,
                )
                or []
            )

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
            [(code, f"{label} ({code})") for label, code in self.TAG_COLOR_CHOICES]
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
            raise InvalidException("Usage: add-note-tags [note-name] [tag[:color] ...]")

        note_name = arguments[0].strip()
        tag_specs = arguments[1:]
        tags = self._parse_tag_specs(tag_specs)

        if not tags:
            tags = self._collect_tags_interactively()

        if not tags:
            raise InvalidException("At least one tag is required")

        updated_note = self.note_service.add_tags(note_name, tags)

        return f"Tags updated. Current tags: {', '.join(updated_note.tag_names())}"

    @command_handler_decorator
    def remove_note_tag(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            raise InvalidException("Usage: remove-note-tag [note-name] [tag-name]")

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
