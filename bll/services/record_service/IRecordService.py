from abc import ABC, abstractmethod
from dal.entities.Record import Record


class IRecordService(ABC):
    @abstractmethod
    def save(self, new_record: Record) -> Record:
        pass

    @abstractmethod
    def update(self, record_name: str, new_record: Record) -> Record:
        pass

    @abstractmethod
    def get_by_name(self, record_name: str) -> Record | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Record] | None:
        pass

    @abstractmethod
    def rename(self, record_name: str, new_name: str) -> Record:
        pass

    @abstractmethod
    def delete(self, record_name: str) -> None:
        pass

    @abstractmethod
    def has(self, record_name: str) -> bool:
        pass

    @abstractmethod
    def get_with_upcoming_birthdays(self) -> list[Record]:
        pass
