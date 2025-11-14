from bll.services.command_service.CommandService import CommandService
from bll.services.input_service.InputService import InputService
from bll.services.pickle_file_service.PickleFileService import PickleFileService
from bll.services.record_service.RecordService import RecordService
from bll.services.note_service.NoteService import NoteService
from dal.file_managers.pickle_file_manager.PickleFileManager import PickleFileManager
from dal.storages.AddressBookStorage import AddressBookStorage
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.NoteStorage import NoteStorage
from dal.entities.Record import Record

from colorama import Fore as cf
from colorama import Style as cs


def main() -> None:
    book_storage = AddressBookStorage()
    record_service = RecordService(book_storage)

    record_file_manager = PickleFileManager[dict[str, Record]]()
    record_file_service = PickleFileService[dict[str, Record]](
        record_file_manager, book_storage
    )

    note_storage = NoteStorage()
    note_service = NoteService(note_storage)

    input_service = InputService()
    command_service = CommandService(
        record_service=record_service,
        file_service=record_file_service,
        note_service=note_service,
        input_service=input_service,
    )

    print("\n🤖 Welcome to the Assistant Bot!")
    print(f"Type '{cf.CYAN}help{cs.RESET_ALL}' to see available commands.\n")

    try:
        latest_file_name = record_file_service.get_latest_file_name()
        if latest_file_name:
            record_file_service.load_by_name(latest_file_name)
            print(f"📂 Loaded last saved state from '{latest_file_name}'")
        else:
            print("📂 No saved state found, starting with empty address book.")
    except Exception as e:
        print(f"⚠️ {cf.YELLOW}Could not load previous state: {e}{cs.RESET_ALL}")

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
