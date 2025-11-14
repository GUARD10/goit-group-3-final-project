from pathlib import Path
import pickle
from dal.file_managers.IFileManager import IFileManager

DEFAULT_BASE_DIR = Path("files")


class PickleFileManager[Data](IFileManager[Data]):
    def __init__(self, base_dir: Path = DEFAULT_BASE_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data, name: str) -> None:
        filename = str(name)
        filepath = self._generate_unique_filename(filename)
        with filepath.open("wb") as file:
            pickle.dump(data, file)

    def load(self, name: str):
        filepath = self._normalize_name(name)
        if not filepath.exists():
            raise FileNotFoundError(f"File '{filepath}' not found")
        with filepath.open("rb") as file:
            return pickle.load(file)

    def delete(self, name: str) -> None:
        filepath = self._normalize_name(name)
        if filepath.exists():
            filepath.unlink()

    def get_all_names(self) -> list[str]:
        return [
            f.name
            for f in self.base_dir.iterdir()
            if f.is_file() and f.suffix == ".pkl"
        ]

    def has_file_with_name(self, name: str) -> bool:
        return self._normalize_name(name).exists()

    def _normalize_name(self, name: str) -> Path:
        name_path = Path(name)
        if name_path.suffix != ".pkl":
            name_path = name_path.with_suffix(".pkl")
        return self.base_dir / name_path.name

    def _generate_unique_filename(self, name: str) -> Path:
        base_path = self._normalize_name(name)
        if not base_path.exists():
            return base_path

        base = base_path.stem
        ext = base_path.suffix

        counter = 1
        while True:
            new_name = self.base_dir / f"{base}_{counter}{ext}"
            if not new_name.exists():
                return new_name
            counter += 1
