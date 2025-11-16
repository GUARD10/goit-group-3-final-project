import calendar
import inspect
from typing import Optional

from colorama import Fore, Style

from bll.decorators.command_handler_decorator import command_handler_decorator
from bll.helpers.calendar_renderer import render_calendar_with_clock
from bll.helpers.table_renderer import (
    render_contact_details,
    render_contacts_table,
    render_note_details,
    render_notes_table,
)
from bll.helpers.tag_palette import TAG_COLORS
from bll.registries.i_registry import IRegistry
from bll.services.command_service.i_command_service import ICommandService
from bll.services.input_service.i_input_service import IInputService
from bll.services.note_service.i_note_service import INoteService
from bll.services.record_service.i_record_service import IRecordService
from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy
from dal.entities.command import Command
from dal.entities.note import Note
from dal.entities.record import Record
from dal.exceptions.exit_bot_error import ExitBotError
from dal.exceptions.invalid_error import InvalidError


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
            # Basic Commands
            "hello": Command("hello", self.hello, "👋 Say hello"),
            "help": Command("help", self.help_command, "❓ Show all commands"),
            "exit": Command("exit", self.exit_bot, "👋 Save & exit"),
            "close": Command("close", self.exit_bot, "👋 Save & exit"),
            "calendar": Command(
                "calendar [month]? [year]?",
                self.show_calendar,
                "📅 View calendar with birthdays",
            ),
            # Contact Commands
            "add-contact": Command(
                "add-contact [contact-name] [phone]",
                self.add_contact,
                "➕ Create new contact with name and phone",
            ),
            "delete-contact": Command(
                "delete-contact [contact-name]",
                self.delete_contact,
                "🗑️ Remove contact completely",
            ),
            "all-contacts": Command(
                "all-contacts",
                self.show_all,
                "📋 Show all your contacts",
            ),
            "show-contact": Command(
                "show-contact [contact-name]",
                self.show_contact,
                "👁️ View contact details",
            ),
            "add-phone": Command(
                "add-phone [contact-name] [phone]",
                self.add_phone,
                "📞 Add another phone to contact",
            ),
            "delete-phone": Command(
                "delete-phone [contact-name] [phone]",
                self.delete_phone,
                "🗑️ Remove phone from contact",
            ),
            "add-email": Command(
                "add-email [contact-name] [email]",
                self.add_email,
                "📧 Add email to contact",
            ),
            "delete-email": Command(
                "delete-email [contact-name] [email]",
                self.delete_email,
                "🗑️ Remove email from contact",
            ),
            "set-address": Command(
                "set-address [contact-name] [address...]",
                self.set_address,
                "🏠 Set contact's address",
            ),
            "clear-address": Command(
                "clear-address [contact-name]",
                self.delete_address,
                "🗑️ Clear contact's address",
            ),
            "add-birthday": Command(
                "add-birthday [contact-name] [DD.MM.YYYY]",
                self.add_birthday,
                "🎂 Set birthday to contact (replaces existing)",
            ),
            "clear-birthday": Command(
                "clear-birthday [contact-name]", self.clear_birthday, "🗑️ Clear birthday"
            ),
            "upcoming-birthdays": Command(
                "upcoming-birthdays [days]?",
                self.birthdays,
                "🎁 Show birthdays in next N days (default: 7)",
            ),
            "search-contacts": Command(
                "search-contacts [text]",
                self.search_contacts,
                "🔍 Find contacts by name, phone, email, etc.",
            ),
            "save-contact": Command(
                "save-contact [file-name]?",
                self.save_contact_state,
                "💾 Save contacts (leave empty for autosave)",
            ),
            "load-contact": Command(
                "load-contact [file-name]",
                self.load_contact_state,
                "📂 Load contacts from file",
            ),
            "delete-contact-file": Command(
                "delete-contact-file [file-name]",
                self.delete_contact_file,
                "🗑️ Delete saved contacts file",
            ),
            "contacts-files": Command(
                "contacts-files",
                self.show_contact_files,
                "📁 List saved contacts files",
            ),
            # Note Commands
            "add-note": Command(
                "add-note [note-name]",
                self.add_note,
                "📝 Create new note",
            ),
            "delete-note": Command(
                "delete-note [note-name]",
                self.delete_note,
                "🗑️ Remove note",
            ),
            "show-note": Command(
                "show-note [note-name]", self.show_note, "👁️ View note details"
            ),
            "all-notes": Command("all-notes", self.show_all_notes, "📚 View all notes"),
            "search-notes": Command(
                "search-notes [text]",
                self.search_notes,
                "🔍 Find notes by content or tags",
            ),
            "edit-note-title": Command(
                "edit-note-title [note-name]",
                self.edit_note_title,
                "✏️ Change note title",
            ),
            "edit-note-content": Command(
                "edit-note-content [note-name]",
                self.edit_note_content,
                "📄 Update note content",
            ),
            "add-note-tags": Command(
                "add-note-tags [note-name] [tag:color]...",
                self.add_note_tags,
                "🏷️ Add colored tags to note",
            ),
            "remove-note-tag": Command(
                "remove-note-tag [note-name] [tag]",
                self.remove_note_tag,
                "❌ Remove tag from note",
            ),
            "show-notes-by-tag": Command(
                "show-notes-by-tag [tag]?",
                self.show_notes_by_tag,
                "🏷️ Filter notes by tag",
            ),
            "save-note": Command(
                "save-note [file-name]?",
                self.save_note_state,
                "💾 Save notes (leave empty for autosave)",
            ),
            "load-note": Command(
                "load-note [file-name]",
                self.load_note_state,
                "📂 Load notes from file",
            ),
            "delete-note-file": Command(
                "delete-note-file [file-name]",
                self.delete_note_file,
                "🗑️ Delete saved notes file",
            ),
            "note-files": Command(
                "note-files", self.show_note_files, "📁 List saved notes files"
            ),
        }

    def execute(self, command_name: str, arguments: list[str]) -> str:
        command = self.get_command(command_name)
        if not command:
            raise InvalidError("Invalid command")

        handler = command.handler
        sig = inspect.signature(handler)
        param_count = len(sig.parameters)

        result = handler() if param_count == 0 else handler(arguments)
        return str(result)  # Explicitly ensure string return

    def get_command(self, command: str) -> Optional[Command]:
        return self.commands.get(command)

    @command_handler_decorator
    def add_contact(self, arguments: list[str]) -> str:
        name, phone = [arg.strip() for arg in arguments]

        if not PhoneValidationPolicy.validate(phone):
            raise InvalidError(PhoneValidationPolicy.error_message(phone))

        new_contact = Record(name, phone)
        self.record_service.save(new_contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Contact added!{Style.RESET_ALL}",
            new_contact,
        )

    @command_handler_decorator
    def add_phone(self, arguments: list[str]) -> str:
        name, new_phone = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name).update().add_phone(new_phone).build()
        )
        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Phone added!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def delete_phone(self, arguments: list[str]) -> str:
        name, phone_to_delete = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name)
            .update()
            .remove_phone(phone_to_delete)
            .build()
        )

        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Phone removed!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def show_contact(self, arguments: list[str]) -> str:
        name = arguments[0]
        contact = self.record_service.get_by_name(name)
        message = (
            f"{Fore.CYAN}📞 {Fore.MAGENTA}{name}{Fore.CYAN} contact:{Style.RESET_ALL}"
        )
        return self._contact_response(message, contact)

    @command_handler_decorator
    def delete_contact(self, arguments: list[str]) -> str:
        name = arguments[0]
        self.record_service.delete(name)
        return f"{Fore.GREEN}✅ Deleted {Fore.MAGENTA}{name}{Style.RESET_ALL}"

    @command_handler_decorator
    def show_all(self) -> str:
        contacts = self.record_service.get_all()
        if not contacts:
            return (
                f"{Fore.YELLOW}📭 No contacts yet. "
                f"Add one with 'add-contact'!{Style.RESET_ALL}"
            )

        title = f"📇 Contacts ({len(contacts)})"
        return render_contacts_table(contacts, title=title)

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
        message = (
            f"{Fore.GREEN}🎂 Birthday set for {Fore.MAGENTA}{name}{Style.RESET_ALL}"
        )
        return self._contact_response(message, updated_contact)

    @command_handler_decorator
    def birthdays(self, arguments: list[str] | None = None) -> str:
        days = 7
        if arguments:
            try:
                days = int(arguments[0])
                if days <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise InvalidError("Please enter a positive number of days")

        contacts_with_upcoming_birthdays = (
            self.record_service.get_with_upcoming_birthdays(days)
        )

        if not contacts_with_upcoming_birthdays:
            return (
                f"{Fore.YELLOW}🎂 No birthdays in the next {days} days{Style.RESET_ALL}"
            )

        summary_lines = [
            f"🎉 {contact.name.value} — {contact.birthday}"
            for contact in contacts_with_upcoming_birthdays
        ]
        title = f"🎁 Upcoming birthdays (next {days} days)"
        table = render_contacts_table(
            contacts_with_upcoming_birthdays,
            title=title,
        )
        summary = "\n".join(summary_lines)
        return f"{summary}\n{table}"

    @command_handler_decorator
    def clear_birthday(self, arguments: list[str]) -> str:
        name = arguments[0]
        updated_contact = (
            self.record_service.get_by_name(name).update().clear_birthday().build()
        )
        self.record_service.update(name, updated_contact)
        message = (
            f"{Fore.GREEN}✅ Birthday cleared for {Fore.MAGENTA}{name}{Style.RESET_ALL}"
        )
        return self._contact_response(message, updated_contact)

    @command_handler_decorator
    def show_calendar(self, arguments: list[str] | None = None) -> str:
        month, year = self._resolve_calendar_arguments(arguments or [])
        contacts = self.record_service.get_all() or []
        return render_calendar_with_clock(contacts, month=month, year=year)

    @command_handler_decorator
    def add_email(self, arguments: list[str]) -> str:
        name, new_email = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name).update().add_email(new_email).build()
        )
        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Email added!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def delete_email(self, arguments: list[str]) -> str:
        name, email_to_delete = [arg.strip() for arg in arguments]

        contact = (
            self.record_service.get_by_name(name)
            .update()
            .remove_email(email_to_delete)
            .build()
        )

        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Email removed!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def set_address(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            raise InvalidError("Usage: set-address [name] [address]")

        name = arguments[0].strip()
        address = " ".join(arg.strip() for arg in arguments[1:])

        contact = (
            self.record_service.get_by_name(name).update().set_address(address).build()
        )
        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Address set!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def delete_address(self, arguments: list[str]) -> str:
        (name,) = [arg.strip() for arg in arguments]

        contact = self.record_service.get_by_name(name).update().clear_address().build()
        self.record_service.update(name, contact)

        return self._contact_response(
            f"{Fore.GREEN}✅ Address cleared!{Style.RESET_ALL}",
            contact,
        )

    @command_handler_decorator
    def hello(self) -> str:
        return f"{Fore.CYAN}👋 Hello! How can I help you today?{Style.RESET_ALL}"

    @command_handler_decorator
    def help_command(self) -> str:
        if not self._help_text:
            sections = {
                "📇 Contacts": [
                    "add-contact",
                    "delete-contact",
                    "show-contact",
                    "all-contacts",
                    "add-phone",
                    "delete-phone",
                    "add-email",
                    "delete-email",
                    "set-address",
                    "clear-address",
                    "search-contacts",
                ],
                "🎂 Birthdays": [
                    "add-birthday",
                    "clear-birthday",
                    "upcoming-birthdays",
                ],
                "📝 Notes": [
                    "add-note",
                    "delete-note",
                    "all-notes",
                    "show-note",
                    "search-notes",
                    "edit-note-title",
                    "edit-note-content",
                    "add-note-tags",
                    "remove-note-tag",
                    "show-notes-by-tag",
                ],
                "💾 Files": [
                    "save-contact",
                    "load-contact",
                    "delete-contact-file",
                    "contacts-files",
                    "save-note",
                    "load-note",
                    "delete-note-file",
                    "note-files",
                ],
                "⚙️ System": ["hello", "help", "exit", "close", "calendar"],
            }
            lines: list[str] = []
            for title, cmds in sections.items():
                lines.append(f"\n{Fore.BLUE}{title}{Style.RESET_ALL}")
                for cmd in cmds:
                    if cmd in self.commands:
                        c = self.commands[cmd]
                        lines.append(
                            f"  {Fore.CYAN}{c.name}{Style.RESET_ALL} — {c.description}"
                        )
            self._help_text = (
                f"{Fore.YELLOW}📋 Available commands:{Style.RESET_ALL}\n"
                + "\n".join(lines)
            )
        return self._help_text

    @command_handler_decorator
    def exit_bot(self) -> None:
        self._save_all_states()

        raise ExitBotError(
            f"\n{Fore.GREEN}👋 Goodbye! All data saved.{Style.RESET_ALL}"
        )

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
            "\n📝 Enter note title (or /cancel to abort)",
            allow_empty=False,
        )
        if note_title is None:
            return f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}"

        note_content = self.input_service.read_multiline(
            header=(
                "\n✏️ Enter note content:\n"
                "  • Type your text (multiple lines OK)\n"
                "  • Press Enter twice when done\n"
                "  • Min 10 characters required\n"
                "  • Type /cancel to abort\n"
            ),
            min_len=10,
        )
        if note_content is None:
            return f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}"

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

        return self._note_response(
            f"{Fore.GREEN}✅ Note created!{Style.RESET_ALL}",
            new_note,
        )

    @command_handler_decorator
    def edit_note_title(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        note = self.note_service.get_by_name(note_name)

        new_title = self.input_service.read_value(
            "\n✏️ Edit title (or /cancel)",
            default=note.title.value,
            allow_empty=False,
        )
        if new_title is None:
            return f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}"

        updated_note = note.update().set_title(new_title).build()
        self.note_service.update(note_name, updated_note)

        return self._note_response(
            f"{Fore.GREEN}✅ Title updated!{Style.RESET_ALL}",
            updated_note,
        )

    @command_handler_decorator
    def edit_note_content(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        note = self.note_service.get_by_name(note_name)

        new_content = self.input_service.read_multiline(
            header=(
                "\n✏️ Enter new content:\n"
                "  • Type your updated content\n"
                "  • Press Enter twice when done\n"
                "  • Type /cancel to abort\n"
            ),
            min_len=10,
            show_existing=note.content.value,
        )
        if new_content is None:
            return f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}"

        updated_note = note.update().set_content(new_content).build()
        self.note_service.update(note_name, updated_note)

        return self._note_response(
            f"{Fore.GREEN}✅ Content updated!{Style.RESET_ALL}",
            updated_note,
        )

    @command_handler_decorator
    def delete_note(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        self.note_service.delete(note_name)
        return (
            f"{Fore.GREEN}✅ Note '{Fore.MAGENTA}{note_name}"
            f"{Fore.GREEN}' deleted.{Style.RESET_ALL}"
        )

    @command_handler_decorator
    def show_all_notes(self) -> str:
        notes = self.note_service.get_all_sorted_by_tags()
        if not notes:
            return (
                f"{Fore.YELLOW}📭 No notes yet. "
                f"Create one with 'add-note'!{Style.RESET_ALL}"
            )
        title = f"📚 Notes ({len(notes)})"
        return render_notes_table(notes, title=title)

    @command_handler_decorator
    def show_note(self, arguments: list[str]) -> str:
        note_name = arguments[0].strip()
        note = self.note_service.get_by_name(note_name)

        message = (
            f"{Fore.CYAN}📝 {Fore.MAGENTA}{note_name}{Fore.CYAN} note:{Style.RESET_ALL}"
        )
        return self._note_response(message, note)

    @command_handler_decorator
    def search_contacts(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.record_service.search(query)

        if not matches:
            return f"{Fore.YELLOW}🔍 No contacts found for '{query}'{Style.RESET_ALL}"

        title = f"🔍 Found {len(matches)} contact(s) matching '{query}'"
        return render_contacts_table(matches, title=title)

    @command_handler_decorator
    def search_notes(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.note_service.search(query)

        if not matches:
            return f"{Fore.YELLOW}🔍 No notes found for '{query}'{Style.RESET_ALL}"

        title = f"🔍 Found {len(matches)} note(s) matching '{query}'"
        return render_notes_table(matches, title=title)

    def _collect_tags_interactively(self) -> list[tuple[str, str | None]]:
        tags: list[tuple[str, str | None]] = []

        existing_tags = self.note_service.get_distinct_tags()
        choices = [
            (
                tag.value,
                f"{tag.value}" + (f" ({tag.color})" if tag.color else ""),
            )
            for tag in existing_tags
        ]

        selected = self.input_service.choose_multiple_from_list(
            "🏷️ Tags",
            (
                "Select existing tags (use TAB + ↑↓ and Enter) or type new ones "
                "(use name:#hex for custom color)"
            ),
            choices,
            allow_custom=True,
        )

        if not selected:
            return []

        color_map = {tag.value.lower(): tag for tag in existing_tags}
        seen: set[str] = set()

        for raw_value in selected:
            raw_value = raw_value.strip()
            if not raw_value:
                continue

            existing = color_map.get(raw_value.lower())
            if existing:
                key = existing.value.lower()
                if key in seen:
                    continue
                seen.add(key)
                tags.append((existing.value, existing.color))
                continue

            if ":" in raw_value:
                name, raw_color = raw_value.split(":", 1)
                color_value: str | None = raw_color.strip() or None
            else:
                name = raw_value
                color_value = self._prompt_tag_color(name)

            name = name.strip()
            if not name:
                continue

            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            tags.append((name, color_value))

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
        options = [("__auto__", "✨ Auto-assign color")]
        options.extend(
            [(code, f"{label} ({code})") for label, code in self.TAG_COLOR_CHOICES]
        )
        options.append(("__custom__", "🎨 Custom color..."))

        choice = self.input_service.choose_from_list(
            f"🎨 Color for '{tag_name}'",
            "Use TAB + ↑↓ and Enter to select",
            options,
        )

        if choice is None:
            manual = self.input_service.read_value(
                "Enter custom color (e.g. #FF00AA) or leave empty",
                allow_empty=True,
            )
            return manual or None

        if choice == "__auto__":
            return None

        if choice == "__custom__":
            return self.input_service.read_value(
                "Enter color (e.g. #FF00AA or teal)", allow_empty=False
            )

        return choice

    @command_handler_decorator
    def add_note_tags(self, arguments: list[str]) -> str:
        if not arguments:
            raise InvalidError("Usage: add-note-tags [note-name] [tag:color ...]")

        note_name = arguments[0].strip()
        tag_specs = arguments[1:]
        tags = self._parse_tag_specs(tag_specs)

        if not tags:
            tags = self._collect_tags_interactively()

        if not tags:
            raise InvalidError("Please add at least one tag")

        updated_note = self.note_service.add_tags(note_name, tags)

        tag_list = ", ".join(t.value for t in updated_note.tags)
        return self._note_response(
            f"{Fore.GREEN}✅ Tags updated: {tag_list}{Style.RESET_ALL}",
            updated_note,
        )

    @command_handler_decorator
    def remove_note_tag(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            raise InvalidError("Usage: remove-note-tag [note-name] [tag]")

        note_name = arguments[0].strip()
        tag_name = arguments[1].strip()
        updated_note = self.note_service.remove_tag(note_name, tag_name)

        return self._note_response(
            f"{Fore.GREEN}✅ Tag '{tag_name}' removed{Style.RESET_ALL}",
            updated_note,
        )

    @command_handler_decorator
    def show_notes_by_tag(self, arguments: list[str]) -> str:
        tag_name = arguments[0].strip() if arguments else None
        if tag_name == "":
            tag_name = None
        notes = self.note_service.get_all_sorted_by_tags(tag_name)

        if not notes:
            if tag_name:
                return f"{Fore.YELLOW}🏷️ No notes with tag '{tag_name}'{Style.RESET_ALL}"
            return f"{Fore.YELLOW}📭 No notes found{Style.RESET_ALL}"

        title = (
            f"🏷️ Notes with tag '{tag_name}'" if tag_name else "📚 Notes sorted by tags"
        )
        return render_notes_table(notes, title=title)

    def _contact_response(
        self, message: str, contact: Record, *, title: str | None = None
    ) -> str:
        table = render_contact_details(contact, title=title)
        return f"{message}\n{table}"

    def _note_response(
        self, message: str, note: Note, *, title: str | None = None
    ) -> str:
        table = render_note_details(note, title=title)
        return f"{message}\n{table}"

    def _resolve_calendar_arguments(
        self, arguments: list[str]
    ) -> tuple[int | None, int | None]:
        if not arguments:
            return None, None

        if len(arguments) == 1:
            single = arguments[0].strip()
            if self._is_year_token(single):
                return None, self._parse_year_argument(single)
            return self._parse_month_argument(single), None

        if len(arguments) == 2:
            month_value = self._parse_month_argument(arguments[0])
            year_value = self._parse_year_argument(arguments[1])
            return month_value, year_value

        raise InvalidError(
            "Usage: calendar [month] [year]\n"
            "Examples: 'calendar', 'calendar March', 'calendar 12 2025'"
        )

    def _parse_month_argument(self, token: str) -> int:
        cleaned = token.strip()
        if not cleaned:
            raise InvalidError("Month cannot be empty")

        try:
            month_value = int(cleaned)
        except ValueError:
            month_lookup = self._month_lookup()
            normalized = cleaned.lower()
            if normalized in month_lookup:
                return month_lookup[normalized]
            raise InvalidError("Invalid month. Use 1-12 or month names (e.g. 'March')")

        if 1 <= month_value <= 12:
            return month_value

        raise InvalidError("Month must be 1-12")

    @staticmethod
    def _parse_year_argument(token: str) -> int:
        cleaned = token.strip()
        if not cleaned or not cleaned.isdigit():
            raise InvalidError("Year must be a number (e.g. 2025)")

        year_value = int(cleaned)
        if year_value < 1900 or year_value > 9999:
            raise InvalidError("Year must be between 1900-9999")

        return year_value

    @staticmethod
    def _is_year_token(token: str) -> bool:
        stripped = token.strip()
        return stripped.isdigit() and len(stripped) == 4

    @staticmethod
    def _month_lookup() -> dict[str, int]:
        lookup: dict[str, int] = {}
        for idx, name in enumerate(calendar.month_name):
            if not name:
                continue
            lookup[name.lower()] = idx
        for idx, name in enumerate(calendar.month_abbr):
            if not name:
                continue
            lookup[name.lower()] = idx
        return lookup

    def _save_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)

        try:
            file_name = arguments[0]
        except IndexError:
            file_name = "autosave"

        file_service.save_with_name(file_name)
        return f"{Fore.GREEN}💾 Saved to '{file_name}'{Style.RESET_ALL}"

    def _load_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)

        file_name = arguments[0]
        file_service.load_by_name(file_name)

        return f"{Fore.GREEN}📂 Loaded from '{file_name}'{Style.RESET_ALL}"

    def _delete_state(self, arguments: list[str], key: str) -> str:
        file_service = self.file_service_registry.get(key)
        file_name = arguments[0]
        file_service.delete_by_name(file_name)
        return f"{Fore.GREEN}✅ File '{file_name}' deleted{Style.RESET_ALL}"

    def _show_all_state_files(self, key: str) -> str:
        file_service = self.file_service_registry.get(key)
        file_names = file_service.get_file_list()

        if not file_names:
            return f"{Fore.YELLOW}📭 No saved files{Style.RESET_ALL}"

        files_list = "\n".join(f"  • {name}" for name in file_names)
        return f"{Fore.CYAN}📁 Available files:{Style.RESET_ALL}\n" + files_list

    def _save_all_states(self) -> None:
        for key, service in self.file_service_registry.get_all().items():
            if service.is_save_able():
                saved_file = service.save_with_name()
                print(f"{Fore.GREEN}💾 [{key}] saved → {saved_file}{Style.RESET_ALL}")
