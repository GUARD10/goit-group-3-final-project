from abc import ABC, abstractmethod

from dal.entities.Note import Note


class INoteService(ABC):
    @abstractmethod
    def add(self, note_name: str, note_title: str, note_content: str) -> Note:
        pass

    @abstractmethod
    def update(self, note_name: str, new_note: Note) -> Note:
        pass

    @abstractmethod
    def get_by_name(self, note_name: str) -> Note:
        pass

    @abstractmethod
    def get_all(self) -> list[Note] | None:
        pass

    @abstractmethod
    def rename(self, note_name: str, new_name: str) -> Note:
        pass

    @abstractmethod
    def delete(self, note_name: str) -> None:
        pass

    @abstractmethod
    def has(self, note_name: str) -> bool:
        pass
