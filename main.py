from pathlib import Path

from bll.configs.config import get_config
from bll.services.command_service.CommandService import CommandService
from bll.services.input_service.InputService import InputService
from bll.services.file_service.FileService import FileService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService
from bll.registries.FileServiceRegistry import FileServiceRegistry

from dal.file_managers.pickle_file_manager.PickleFileManager import PickleFileManager
from dal.file_managers.json_file_manager.JsonFileManager import JsonFileManager
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.NoteStorage import NoteStorage
from dal.entities.Record import Record
from dal.entities.Note import Note

from colorama import Fore as cf
from colorama import Style as cs


def main() -> None:
    config = get_config()

    book_storage = AddressBookStorage()
    note_storage = NoteStorage()

    # Choose backend per config
    if config.backend == "json":
        contact_file_manager = JsonFileManager[dict[str, Record]](config.contacts_dir)
        note_file_manager = JsonFileManager[dict[str, Note]](config.notes_dir)
    else:
        contact_file_manager = PickleFileManager[dict[str, Record]](config.contacts_dir)
        note_file_manager = PickleFileManager[dict[str, Note]](config.notes_dir)

    contact_file_service = FileService[dict[str, Record]](
        contact_file_manager, book_storage
    )
    note_file_service = FileService[dict[str, Note]](
        note_file_manager, note_storage
    )

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

    print("\n🤖 Welcome to the Assistant Bot!")
    print(f"Type '{cf.CYAN}help{cs.RESET_ALL}' to see available commands.\n")

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
            user_input = input("Enter a command: ").strip()

            if not user_input:
                continue

            command_name, arguments = input_service.handle(user_input)
            result = command_service.execute(command_name, arguments)
            print(result)

        except InvalidException as ic:
            print(f"{cf.RED}{ic}{cs.RESET_ALL}")
            continue
        except AlreadyExistException as aee:
            print(f"{cf.RED}{aee}{cs.RESET_ALL}")
        except NotFoundException as nf:
            print(f"{cf.RED}{nf}{cs.RESET_ALL}")
        except KeyboardInterrupt:
            try:
                result = command_service.execute("exit", [])
                if result:
                    print(result)
            except ExitBotException as eb:
                print(f"{cf.RED}{eb}{cs.RESET_ALL}")
            break
        except ExitBotException as eb:
            print(f"{cf.RED}{eb}{cs.RESET_ALL}")
            break
        except Exception as ex:
            print(f"💥 {cf.RED}Unexpected error: {ex}{cs.RESET_ALL}")
            break


if __name__ == "__main__":
    main()
