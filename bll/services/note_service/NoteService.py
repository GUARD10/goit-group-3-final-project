from dal.entities.Note import Note
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.IStorage import IStorage

from bll.services.note_service.INoteService import INoteService
from bll.helpers.SearchHelper import SearchHelper
from bll.helpers.TagPalette import TAG_COLOR_CODES
from dal.entities.Tag import Tag
from typing import Sequence
from datetime import datetime


class NoteService(INoteService):
    COLOR_PALETTE = TAG_COLOR_CODES

    def __init__(self, storage: IStorage[str, Note]):
        self.storage = storage

    def add(
        self,
        note_name: str,
        note_title: str,
        note_content: str,
        tags: Sequence[tuple[str, str | None] | str] | None = None,
    ) -> Note:
        self._validate_note_fields(note_name, note_title, note_content)

        if self.has(note_name):
            raise AlreadyExistException(f"Note '{note_name}' already exists")

        tag_list = self._prepare_tags(tags)
        new_note = Note(note_name, note_title, note_content, tags=tag_list)
        self.storage.add(new_note)

        return new_note

    def update(self, note_name: str, new_note: Note) -> Note:
        self._validate_note(new_note)

        if not self.has(note_name):
            raise NotFoundException(f"Note '{note_name}' not found")

        self.storage.update_item(note_name, new_note)

        return new_note

    def get_by_name(self, note_name: str) -> Note:
        note = self.storage.find(note_name)

        if not note:
            raise NotFoundException(f"Note '{note_name}' not found")

        return note

    def get_all(self) -> list[Note]:
        return self.storage.all_values() or []

    def rename(self, note_name: str, new_name: str) -> Note:
        if not self.has(note_name):
            raise NotFoundException(f"Note '{note_name}' not found")

        note = self.get_by_name(note_name)
        note.name.value = new_name

        self.delete(note_name)
        self.add(
            note.name.value,
            note.title.value,
            note.content.value,
            tags=[(tag.value, tag.color) for tag in note.tags],
        )

        return self.get_by_name(new_name)

    def delete(self, note_name: str) -> None:
        if not self.has(note_name):
            raise NotFoundException(f"Note '{note_name}' not found")

        self.storage.delete(note_name)

    def has(self, note_name: str) -> bool:
        self._validate_note_name(note_name)
        return self.storage.has(note_name)

    def search(self, query: str) -> list[Note]:
        tokens = SearchHelper.prepare_tokens(query)

        def is_match(note: Note) -> bool:
            return SearchHelper.match_all_tokens(note, tokens)

        return self.storage.filter(is_match)

    def add_tags(
        self, note_name: str, tags: Sequence[tuple[str, str | None] | str]
    ) -> Note:
        normalized = self._prepare_tags(tags)
        if not normalized:
            raise InvalidException("Tags list cannot be empty")

        note = self.get_by_name(note_name)
        for tag in normalized:
            note.add_tag(tag)
        note.updated_at = datetime.now()
        self.storage.update_item(note_name, note)
        return note

    def remove_tag(self, note_name: str, tag_name: str) -> Note:
        note = self.get_by_name(note_name)
        normalized = self._normalize_tag_name(tag_name)
        removed = note.remove_tag(normalized)
        if not removed:
            raise NotFoundException(f"Tag '{tag_name}' not found in note '{note_name}'")
        note.updated_at = datetime.now()
        self.storage.update_item(note_name, note)
        return note

    def get_by_tag(self, tag_name: str) -> list[Note]:
        normalized = self._normalize_tag_name(tag_name)
        return [note for note in self.get_all() if note.has_tag(normalized)]

    def get_all_sorted_by_tags(self, tag_name: str | None = None) -> list[Note]:
        notes = self.get_all()
        if tag_name:
            normalized = self._normalize_tag_name(tag_name)
            notes = [note for note in notes if note.has_tag(normalized)]

        return sorted(
            notes,
            key=lambda n: (n.tags_sort_key(), n.title.value.lower()),
        )

    def get_distinct_tags(self) -> list[Tag]:
        unique: dict[str, Tag] = {}
        for note in self.get_all():
            for tag in note.tags:
                key = tag.value.lower()
                if key not in unique:
                    unique[key] = Tag(tag.value, tag.color)

        return sorted(unique.values(), key=lambda t: t.value.lower())

    @staticmethod
    def _validate_note_name(note_name: str) -> None:
        if not isinstance(note_name, str):
            raise InvalidException("Note name has invalid type")

        if not note_name.strip():
            raise InvalidException("Note name cannot be empty")

    @staticmethod
    def _validate_note_fields(
        note_name: str, note_title: str, note_content: str
    ) -> None:
        if not isinstance(note_name, str):
            raise InvalidException("Note name has invalid type")

        if not note_name.strip():
            raise InvalidException("Note name cannot be empty")

        if not isinstance(note_title, str):
            raise InvalidException("Note title has invalid type")

        if not note_title.strip():
            raise InvalidException("Note name cannot be empty")

        if not isinstance(note_content, str):
            raise InvalidException("Note content has invalid type")

    @staticmethod
    def _validate_note(note: Note) -> None:
        if not isinstance(note, Note):
            raise InvalidException("Record has invalid type")

        if note is None:
            raise NotFoundException("Note cannot be None")

    def _prepare_tags(
        self, tags: Sequence[Tag | tuple[str, str | None] | str] | None
    ) -> list[tuple[str, str | None]]:
        prepared: list[tuple[str, str | None]] = []

        if not tags:
            return prepared

        for raw in tags:
            if isinstance(raw, Tag):
                name = self._normalize_tag_name(raw.value)
                prepared.append((name, raw.color or self._auto_color(name)))
                continue

            if isinstance(raw, tuple):
                if len(raw) != 2:
                    raise InvalidException("Tag tuple must contain (name, color)")
                name, color = raw
            else:
                name, color = str(raw), None

            name = self._normalize_tag_name(name)
            prepared.append((name, self._assign_color(name, color)))

        # deduplicate by name (preserve first occurrence color)
        seen: set[str] = set()
        unique_tags: list[tuple[str, str | None]] = []
        for name, color in prepared:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_tags.append((name, color))

        return unique_tags

    def _assign_color(self, tag_name: str, color: str | None) -> str:
        if color:
            color = color.strip()
            return color or self._auto_color(tag_name)
        return self._auto_color(tag_name)

    def _auto_color(self, tag_name: str) -> str:
        index = sum(ord(ch) for ch in tag_name) % len(self.COLOR_PALETTE)
        return self.COLOR_PALETTE[index]

    @staticmethod
    def _normalize_tag_name(tag_name: str) -> str:
        if not isinstance(tag_name, str):
            raise InvalidException("Tag name has invalid type")

        normalized = tag_name.strip()
        if not normalized:
            raise InvalidException("Tag name cannot be empty")

        return normalized
