from colorama import Fore, Style
from colorama import init as colorama_init

from bll.configs.config import get_config
from bll.registries.file_service_registry import FileServiceRegistry
from bll.services.command_service.command_service import CommandService
from bll.services.file_service.file_service import FileService
from bll.services.input_service.input_service import InputService
from bll.services.note_service.note_service import NoteService
from bll.services.record_service.record_service import RecordService
from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy
from dal.entities.note import Note
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.exit_bot_error import ExitBotError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError
from dal.file_managers.pickle_file_manager.pickle_file_manager import PickleFileManager
from dal.storages.address_book_storage import AddressBookStorage
from dal.storages.note_storage import NoteStorage

from prompt_toolkit import PromptSession
from bll.helpers.PromptCompleter import PromptCompleter


def main() -> None:
    colorama_init(autoreset=False)

    config = get_config()

    PhoneValidationPolicy.set_region(config.phone_region)

    book_storage = AddressBookStorage()
    note_storage = NoteStorage()

    contact_file_manager = PickleFileManager[dict[str, Record]](config.contacts_dir)
    note_file_manager = PickleFileManager[dict[str, Note]](config.notes_dir)


    contact_file_service = FileService[dict[str, Record]](
        contact_file_manager, book_storage
    )
    note_file_service = FileService[dict[str, Note]](note_file_manager, note_storage)

    record_service = RecordService(book_storage)
    note_service = NoteService(note_storage)

    file_service_registry = FileServiceRegistry(contact_file_service, note_file_service)

    input_service = InputService()

    command_service = CommandService(
        record_service=record_service,
        file_service_registry=file_service_registry,
        note_service=note_service,
        input_service=input_service,
    )

    completer = PromptCompleter(
        command_service=command_service,
        record_service=record_service,
        note_service=note_service,
    )

    session: PromptSession = PromptSession(completer=completer)

    print("\n🤖 Welcome to the Assistant Bot!")
    print(f"Type '{Fore.CYAN}help{Style.RESET_ALL}' to see available commands.\n")

    for key, service in file_service_registry.get_all().items():
        try:
            latest_file_name = service.get_latest_file_name()
            if latest_file_name:
                service.load_by_name(latest_file_name)
                print(f"📂 {key} loaded last saved state from '{latest_file_name}'")
            else:
                print(f"📂 {key} no saved state found — starting empty.")
        except Exception as e:
            print(f"⚠️ {key} could not load previous state: {e}")

    while True:
        try:
            user_input = session.prompt("Enter a command: ")

            if not user_input or not user_input.strip():
                continue

            command_name, arguments = input_service.handle(user_input)
            result = command_service.execute(command_name, arguments)
            if result is not None:
                print(result)

        except InvalidError as ic:
            print(f"{Fore.RED}{ic}{Style.RESET_ALL}")
            continue
        except AlreadyExistsError as aee:
            print(f"{Fore.RED}{aee}{Style.RESET_ALL}")
        except NotFoundError as nf:
            print(f"{Fore.RED}{nf}{Style.RESET_ALL}")
        except KeyboardInterrupt:
            try:
                result = command_service.execute("exit", [])
                if result:
                    print(result)
            except ExitBotError as eb:
                print(f"{Fore.RED}{eb}{Style.RESET_ALL}")
            break
        except ExitBotError as eb:
            print(f"{Fore.RED}{eb}{Style.RESET_ALL}")
            break
        except Exception as ex:
            print(f"💥 {Fore.RED}Unexpected error: {ex}{Style.RESET_ALL}")
            break


if __name__ == "__main__":
    main()
