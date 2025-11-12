from typing import Optional

from bll.services.command_service.ICommandService import ICommandService
from bll.services.pickle_file_service.IPickleFileService import IPickleFileService
from bll.services.record_service.IRecordService import IRecordService
from dal.entities.Command import Command
from dal.entities.Record import Record
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from bll.decorators.CommandHandlerDecorator import command_handler_decorator
from dal.storages.IStorage import IStorage

Data = IStorage[str, Record]


class CommandService(ICommandService):  # сервіс трохи роздутий і потребує рефакторингу
    def __init__(
        self, record_service: IRecordService, file_service: IPickleFileService[Data]
    ) -> None:
        self.record_service = record_service
        self.file_service = file_service
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
            ),  # оце має сенс переробити на show-contact і показувати всю інфу по контакту замість чогось конкртеного
            "show-all-contacts": Command(
                "show-all-contacts", self.show_all, "Show all contacts"
            ),
            "help": Command("help", self.help_command, "Show this help message"),
            "exit": Command("exit", self.exit_bot, "Exit the program"),
            "close": Command("close", self.exit_bot, "Close the program"),
            "add-birthday": Command(
                "add-birthday",
                self.add_birthday,
                "Add birthday to contact: add-birthday [name] [birthday]. Note it will replace birthday if exist",
            ),
            "show-birthday": Command(
                "show-birthday",
                self.show_birthday,
                "Show birthday to contact: show-birthday [name]",
            ),  # те саме що і show-phone
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
        }

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
            [
                f"Contact: {contact.name} - {contact.birthday}"
                for contact in contacts_with_upcoming_birthdays
            ]
        )

    @command_handler_decorator
    def show_all(self) -> str:
        contacts = self.record_service.get_all()

        if not contacts:
            return "No contacts found."

        return "\n".join([f"{contact}" for contact in contacts])

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
            }
            lines = []
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
    def delete_contact(self, arguments: list[str]) -> str:
        name = arguments[0]
        self.record_service.delete(name)
        return f"Contact '{name}' deleted."

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

    def get_command(self, command: str) -> Optional[Command]:
        return self.commands.get(command)

    @command_handler_decorator
    def search_contacts(self, arguments: list[str]) -> str:
        query = " ".join(arguments).strip()
        matches = self.record_service.search(query)

        if not matches:
            return "No matching contacts found."

        return "\n".join([f"{contact}" for contact in matches])
