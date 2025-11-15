from collections import UserDict
from typing import Callable

from dal.entities.record import Record
from dal.exceptions.invalid_error import InvalidError
from dal.storages.i_serializable_storage import ISerializableStorage
from dal.storages.i_storage import IStorage


class AddressBookStorage(
    UserDict, IStorage[str, Record], ISerializableStorage[dict[str, Record]]
):
    def __init__(self):
        super().__init__()

    def add(self, record: Record) -> Record:
        self.data[record.name.value] = record
        return record

    def update_item(self, record_name: str, new_record: Record) -> Record:
        self.data[record_name] = new_record
        return new_record

    def find(self, record_name: str) -> Record | None:
        return self.data.get(record_name)

    def all_values(self) -> list[Record]:
        return list(self.data.values())

    def delete(self, record_name: str) -> None:
        self.data.pop(record_name, None)

    def has(self, record_name: str) -> bool:
        return record_name in self.data

    def filter(self, predicate: Callable[[Record], bool]) -> list[Record]:
        return [record for record in self.data.values() if predicate(record)]

    def export_state(self) -> dict[str, Record]:
        return self.data

    def import_state(self, state: dict[str, Record]) -> None:
        if not isinstance(state, dict):
            type_name = type(state).__name__
            raise InvalidError(
                f"Invalid state type: expected dict[str, Record], got {type_name}"
            )

        self.data = state
