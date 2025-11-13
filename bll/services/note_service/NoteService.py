from dal.entities.Note import Note
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.IStorage import IStorage

from bll.services.note_service.INoteService import INoteService


class NoteService(INoteService):
    def __init__(self, storage: IStorage[str, Note]):
        self.storage = storage

    def add(self, note_name: str, note_title: str, note_content: str) -> Note:
        self._validate_note_fields(note_name, note_title, note_content)

        if self.has(note_name):
            raise AlreadyExistException(f"Note '{note_name}' already exists")

        new_note = Note(note_name, note_title, note_content)
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

    def get_all(self) -> list[Note] | None:
        return self.storage.all_values()

    def rename(self, note_name: str, new_name: str) -> Note:
        if not self.has(note_name):
            raise NotFoundException(f"Note '{note_name}' not found")

        note = self.get_by_name(note_name)
        note.name.value = new_name

        self.delete(note_name)
        self.add(note.name.value, note.title.value, note.content.value)

        return note

    def delete(self, note_name: str) -> None:
        if not self.has(note_name):
            raise NotFoundException(f"Note '{note_name}' not found")

        self.storage.delete(note_name)

    def has(self, note_name: str) -> bool:
        self._validate_note_name(note_name)
        return self.storage.has(note_name)

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
