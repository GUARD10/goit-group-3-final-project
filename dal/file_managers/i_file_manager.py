from abc import ABC, abstractmethod


class IFileManager[Data](ABC):
    @abstractmethod
    def save(self, data: Data, name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> Data:
        pass

    @abstractmethod
    def delete(self, name: str) -> None:
        pass

    @abstractmethod
    def get_all_names(self) -> list[str]:
        pass

    @abstractmethod
    def has_file_with_name(self, name: str) -> bool:
        pass
