from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class ISerializableStorage(ABC, Generic[T]):
    @abstractmethod
    def export_state(self) -> T:
        pass

    @abstractmethod
    def import_state(self, state: T) -> None:
        pass
