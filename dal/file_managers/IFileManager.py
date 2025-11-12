from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class IFileManager(ABC, Generic[T]):
    @abstractmethod
    def save(self, obj: T, name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> T:
        pass

    @abstractmethod
    def delete (self, name: str) -> None:
        pass

    @abstractmethod
    def get_all_names(self) -> list[str]:
        pass

    @abstractmethod
    def has_file_with_name(self, name: str) -> bool:
        pass