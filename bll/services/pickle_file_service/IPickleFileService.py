from abc import ABC, abstractmethod


class IPickleFileService(ABC):
    @abstractmethod
    def save_with_name(self, name: str = "autosave") -> str:
        pass

    @abstractmethod
    def load_by_name(self, name: str) -> None:
        pass

    @abstractmethod
    def delete_by_name(self, name: str) -> None:
        pass

    @abstractmethod
    def get_file_list(self) -> list[str]:
        pass

    @abstractmethod
    def get_latest_file_name(self) -> str:
        pass

    @abstractmethod
    def is_save_able(self) -> bool:
        pass
