from datetime import datetime

from dal.entities.Content import Content
from dal.entities.Name import Name
from dal.entities.Title import Title


class Note:
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name: str, title: str, content: str):
        self.name = Name(name)
        self.title = Title(title)
        self.content = Content(content)
        self.created_at = datetime.now()
        self.updated_at: datetime | None = None

    def __hash__(self) -> int:
        return hash((self.name, self.title, self.content))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return (
            self.name == other.name
            and self.title == other.title
            and self.content == other.content
        )

    def __str__(self):
        header = f"📓 {self.title}"
        meta = (
            f"Name: {self.name} | "
            f"Created at: {self.created_at.strftime(self.DATETIME_FORMAT)} | "
            f"Updated at: {self.updated_at.strftime(self.DATETIME_FORMAT) if self.updated_at else 'Never'}"
        )
        divider = "─" * 70
        body = str(self.content)

        return f"\n{header}\n{meta}\n{divider}\n{body}\n{divider}\n"

    def update(self):
        from dal.entity_builders.note_builder.NoteBuilder import NoteBuilder

        return NoteBuilder(self)
