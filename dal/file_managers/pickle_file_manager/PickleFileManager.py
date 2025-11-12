import os
import pickle

from dal.file_managers.IFileManager import IFileManager


class PickleFileManager[Data](IFileManager[Data]):
    def __init__(self, base_dir: str = "files"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, data: Data, name: str) -> None:
        filename = str(name)
        filepath = self._generate_unique_filename(filename)
        with open(filepath, "wb") as file:
            pickle.dump(data, file)

    def load(self, name: str) -> Data:
        filepath = self._normalize_name(name)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' not found")
        with open(filepath, "rb") as file:
            return pickle.load(file)

    def delete(self, name: str) -> None:
        filepath = self._normalize_name(name)
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_all_names(self) -> list[str]:
        return [f for f in os.listdir(self.base_dir) if f.endswith(".pkl")]

    def has_file_with_name(self, name: str) -> bool:
        return os.path.exists(self._normalize_name(name))

    def _normalize_name(self, name: str) -> str:
        base, ext = os.path.splitext(name)
        if not ext:
            ext = ".pkl"
        return os.path.join(self.base_dir, base + ext)

    def _generate_unique_filename(self, name: str) -> str:
        full_path = self._normalize_name(name)
        counter = 1
        while os.path.exists(full_path):
            base, ext = os.path.splitext(name)
            full_path = os.path.join(self.base_dir, f"{base}_{counter}{ext}")
            counter += 1
        return full_path
