import pickle
from datetime import datetime

from bll.services.file_service.i_file_service import IFileService
from dal.exceptions.invalid_error import InvalidError
from dal.file_managers.i_file_manager import IFileManager
from dal.storages.i_serializable_storage import ISerializableStorage


class FileService[Data](IFileService):
    def __init__(
        self, file_manager: IFileManager[Data], storage: ISerializableStorage[Data]
    ) -> None:
        self.file_manager = file_manager
        self.storage = storage
        self._last_loaded_bytes: bytes | None = None
        self._last_loaded_name: str | None = None

    def save_with_name(self, name: str = "autosave") -> str:
        self._validate_name(name)
        data_to_save = self.storage.export_state()

        if not data_to_save:
            raise InvalidError("Data to save cannot be None or empty")

        try:
            current_bytes = pickle.dumps(data_to_save)
        except Exception as e:
            raise InvalidError(f"Cannot serialize data: {e}")

        if self._last_loaded_bytes == current_bytes:
            # Немає змін — не перезаписуємо
            return self._last_loaded_name or name

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not name.endswith(".pkl"):
            name = f"{name}_{timestamp}.pkl"

        self.file_manager.save(data_to_save, name)
        self._last_loaded_bytes = current_bytes
        self._last_loaded_name = name
        return name

    def load_by_name(self, name: str) -> None:
        self._validate_name(name)

        if not self.file_manager.has_file_with_name(name):
            raise InvalidError(f"File with name '{name}' does not exist")

        loaded_data = self.file_manager.load(name)
        self.storage.import_state(loaded_data)
        self._last_loaded_bytes = pickle.dumps(loaded_data)
        self._last_loaded_name = name

    def is_save_able(self) -> bool:
        data_to_save = self.storage.export_state()
        if not data_to_save:
            return False
        try:
            current_bytes = pickle.dumps(data_to_save)
            return current_bytes != self._last_loaded_bytes
        except Exception:
            return True

    def get_file_list(self) -> list[str]:
        names = self.file_manager.get_all_names()
        if not names:
            raise InvalidError("No files available")
        return names

    def get_latest_file_name(self) -> str:
        names = self.get_file_list()
        return sorted(names)[-1]

    def delete_by_name(self, name: str) -> None:
        self._validate_name(name)
        if not self.file_manager.has_file_with_name(name):
            raise InvalidError(f"File with name '{name}' does not exist")
        self.file_manager.delete(name)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(name, str):
            raise InvalidError("File name must be a string")
        if not name or not name.strip():
            raise InvalidError("File name cannot be empty or whitespace")









