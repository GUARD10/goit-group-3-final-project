from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
K = TypeVar("K")

class IStorage(ABC, Generic[K, T]):
    @abstractmethod
    def add(self, item: T) -> T:
        pass

    @abstractmethod
    def update_item(self, key: K, item: T) -> T:
        pass

    @abstractmethod
    def find(self, key: str) -> T | None:
        pass

    @abstractmethod
    def delete(self, key: K) -> None:
        pass

    @abstractmethod
    def has(self, key: K) -> bool:
        pass

    @abstractmethod
    def all_values(self) -> list[T]:
        pass

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        pass
