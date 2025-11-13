from abc import ABC, abstractmethod
from typing import Optional, Sequence

from dal.entities.Note import Note
from dal.entities.Tag import Tag


class INoteService(ABC):
    @abstractmethod
    def add(
        self,
        note_name: str,
        note_title: str,
        note_content: str,
        tags: Sequence[tuple[str, Optional[str]] | str] | None = None,
    ) -> Note:
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

    @abstractmethod
    def search(self, query: str) -> list[Note]:
        pass

    @abstractmethod
    def add_tags(self, note_name: str, tags: Sequence[tuple[str, Optional[str]] | str]) -> Note:
        pass

    @abstractmethod
    def remove_tag(self, note_name: str, tag_name: str) -> Note:
        pass

    @abstractmethod
    def get_by_tag(self, tag_name: str) -> list[Note]:
        pass

    @abstractmethod
    def get_all_sorted_by_tags(self, tag_name: str | None = None) -> list[Note]:
        pass

    @abstractmethod
    def get_distinct_tags(self) -> list[Tag]:
        pass
