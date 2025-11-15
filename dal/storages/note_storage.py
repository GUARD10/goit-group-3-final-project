from collections import UserDict
from typing import Callable

from dal.entities.note import Note
from dal.exceptions.invalid_error import InvalidError
from dal.storages.i_serializable_storage import ISerializableStorage
from dal.storages.i_storage import IStorage


class NoteStorage(UserDict, IStorage[str, Note], ISerializableStorage[dict[str, Note]]):
    def add(self, note: Note) -> Note:
        self.data[note.name.value] = note
        return note

    def update_item(self, note_name: str, note: Note) -> Note:
        self.data[note_name] = note
        return note

    def find(self, note_name: str) -> Note | None:
        return self.data.get(note_name)

    def delete(self, note_name: str) -> None:
        self.data.pop(note_name, None)

    def has(self, note_name: str) -> bool:
        return note_name in self.data

    def all_values(self) -> list[Note]:
        return list(self.data.values())

    def filter(self, predicate: Callable[[Note], bool]) -> list[Note]:
        return [note for note in self.data.values() if predicate(note)]

    def export_state(self) -> dict[str, Note]:
        return self.data

    def import_state(self, state: dict[str, Note]) -> None:
        if not isinstance(state, dict):
            type_name = type(state).__name__
            raise InvalidError(
                f"Invalid state type: expected dict[str, Note], got {type_name}"
            )

        self.data = state
