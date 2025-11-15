from abc import ABC, abstractmethod
from typing import Callable


class IStorage[Key, Item](ABC):
    @abstractmethod
    def add(self, item: Item) -> Item:
        pass

    @abstractmethod
    def update_item(self, key: Key, item: Item) -> Item:
        pass

    @abstractmethod
    def find(self, key: str) -> Item | None:
        pass

    @abstractmethod
    def delete(self, key: Key) -> None:
        pass

    @abstractmethod
    def has(self, key: Key) -> bool:
        pass

    @abstractmethod
    def all_values(self) -> list[Item]:
        pass

    @abstractmethod
    def filter(self, predicate: Callable[[Item], bool]) -> list[Item]:
        pass









