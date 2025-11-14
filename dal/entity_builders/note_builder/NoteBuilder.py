from dal.entities.Content import Content
from dal.entities.Name import Name
from dal.entities.Note import Note
from dal.entities.Title import Title
from typing import Sequence


class NoteBuilder:
    def __init__(self, note: Note):
        self._note = note

    def set_name(self, name: str) -> "NoteBuilder":
        self._note.name = Name(name)
        return self

    def set_title(self, title: str) -> "NoteBuilder":
        self._note.title = Title(title)
        return self

    def set_content(self, content: str) -> "NoteBuilder":
        self._note.content = Content(content)
        return self

    def add_tag(self, tag_name: str, color: str | None = None) -> "NoteBuilder":
        self._note.add_tag(tag_name, color)
        return self

    def remove_tag(self, tag_name: str) -> "NoteBuilder":
        self._note.remove_tag(tag_name)
        return self

    def set_tags(self, tags: Sequence[tuple[str, str | None] | str]) -> "NoteBuilder":
        self._note.set_tags(tags)
        return self

    def build(self) -> Note:
        if not self._note.name or not self._note.title or not self._note.content:
            raise ValueError(
                "Name, Title, and Content must be set before building the Note."
            )

        self._note.updated_at = self._note.created_at

        return self._note
