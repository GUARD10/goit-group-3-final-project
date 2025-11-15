from datetime import datetime
from typing import Sequence

from dal.entities.content import Content
from dal.entities.name import Name
from dal.entities.tag import Tag
from dal.entities.title import Title


class Note:
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        name: str,
        title: str,
        content: str,
        tags: Sequence[Tag | tuple[str, str | None] | str] | None = None,
    ):
        self.name = Name(name)
        self.title = Title(title)
        self.content = Content(content)
        self.created_at = datetime.now()
        self.updated_at: datetime | None = None
        self.tags: list[Tag] = []

        if tags:
            self.set_tags(tags)

    def __hash__(self) -> int:
        return hash((self.name, self.title, self.content, tuple(self.tags)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return (
            self.name == other.name
            and self.title == other.title
            and self.content == other.content
            and self.tags == other.tags
        )

    def __str__(self):
        header = f"📓 {self.title}"
        created = self.created_at.strftime(self.DATETIME_FORMAT)
        updated = (
            self.updated_at.strftime(self.DATETIME_FORMAT)
            if self.updated_at
            else "Never"
        )
        meta = f"Name: {self.name} | Created at: {created} | Updated at: {updated}"
        tags_line = "Tags: " + (
            ", ".join(str(tag) for tag in self.tags) if self.tags else "None"
        )
        divider = "─" * 70
        body = str(self.content)

        return f"\n{header}\n{meta}\n{tags_line}\n{divider}\n{body}\n{divider}\n"

    def update(self):
        from bll.entity_builders.note_builder.note_builder import NoteBuilder

        return NoteBuilder(self)

    def set_tags(self, tags: Sequence[Tag | tuple[str, str | None] | str]) -> "Note":
        self.tags = []
        for raw in tags:
            self._append_tag(raw)
        self._sort_tags()
        return self

    def add_tag(
        self, tag: Tag | tuple[str, str | None] | str, color: str | None = None
    ) -> "Note":
        normalized = self._build_tag(tag, color)
        index = self._find_tag_index(normalized.value)
        if index is not None:
            existing = self.tags[index]
            if normalized.color:
                existing.color = normalized.color
        else:
            self.tags.append(normalized)
        self._sort_tags()
        return self

    def remove_tag(self, tag_name: str) -> bool:
        index = self._find_tag_index(tag_name)
        if index is None:
            return False
        self.tags.pop(index)
        return True

    def has_tag(self, tag_name: str) -> bool:
        return self._find_tag_index(tag_name) is not None

    def tag_names(self) -> list[str]:
        return [tag.value for tag in self.tags]

    def primary_tag(self) -> Tag | None:
        return self.tags[0] if self.tags else None

    def tags_sort_key(self) -> str:
        primary = self.primary_tag()
        return primary.value.lower() if primary else "~"

    def _append_tag(self, tag: Tag | tuple[str, str | None] | str) -> None:
        normalized = self._build_tag(tag)
        if self._find_tag_index(normalized.value) is None:
            self.tags.append(normalized)

    @staticmethod
    def _build_tag(
        tag: Tag | tuple[str, str | None] | str, color: str | None = None
    ) -> Tag:
        if isinstance(tag, Tag):
            resolved_color = tag.color if tag.color is not None else color
            return Tag(tag.value, resolved_color)

        if isinstance(tag, tuple):
            name, maybe_color = tag
            if maybe_color is None:
                maybe_color = color
            return Tag(name, maybe_color)

        return Tag(str(tag), color)

    def _find_tag_index(self, tag_name: str) -> int | None:
        normalized = tag_name.lower().strip()
        for idx, tag in enumerate(self.tags):
            if tag.value.lower() == normalized:
                return idx
        return None

    def _sort_tags(self) -> None:
        self.tags.sort(key=lambda tag: tag.value.lower())









