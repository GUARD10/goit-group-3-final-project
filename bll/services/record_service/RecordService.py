from datetime import date

from bll.helpers.DateHelper import DateHelper
from bll.services.record_service.IRecordService import IRecordService
from dal.entities.Record import Record
from dal.exceptions.AlreadyExistException import AlreadyExistException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from dal.storages.IStorage import IStorage


class RecordService(IRecordService):
    def __init__(self, storage: IStorage[str, Record]):
        self.storage = storage

    def save(self, new_record: Record) -> Record:
        self._validate_record(new_record)

        if self.has(new_record.name.value):
            raise AlreadyExistException(
                f"Record '{new_record.name.value}' already exists"
            )

        self.storage.add(new_record)

        return new_record

    def update(self, record_name: str, new_record: Record) -> Record:
        self._validate_record(new_record)

        if not self.has(record_name):
            raise NotFoundException(f"Record '{record_name}' not found")

        self.storage.update_item(record_name, new_record)

        return new_record

    def get_by_name(self, record_name: str) -> Record:
        record = self.storage.find(record_name)

        if not record:
            raise NotFoundException(f"Record '{record_name}' does not exist")

        return record

    def get_all(self) -> list[Record]:
        return self.storage.all_values()

    def rename(self, record_name: str, new_name: str) -> Record:
        if not self.has(record_name):
            raise NotFoundException(f"Record '{record_name}' not found")

        record = self.get_by_name(record_name)
        record.name.value = new_name

        self.delete(record_name)
        self.save(record)

        return record

    def delete(self, record_name: str) -> None:
        if not self.has(record_name):
            raise NotFoundException(f"Record '{record_name}' not found")

        self.storage.delete(record_name)

    def has(self, record_name: str) -> bool:
        self._validate_record_name(record_name)
        return self.storage.has(record_name)

    def get_with_upcoming_birthdays(self, days: int = 7) -> list[Record]:
        def is_birthday_within_week(record: Record) -> bool:
            # record.birthday може бути None, тому перевіряємо явно
            if record.birthday is None or record.birthday.value is None:
                return False

            birthday_value = record.birthday.value
            return DateHelper.is_date_within_next_week(
                birthday_value, today=date.today(), days=days
            )

        records = self.storage.filter(is_birthday_within_week)

        def next_birthday_date(record: Record) -> date | None:
            if record.birthday is None or record.birthday.value is None:
                return None

            bday = record.birthday.value
            today_date = date.today()
            adjusted = DateHelper.set_date_with_feb_edge_case(bday, today_date.year)

            if adjusted < today_date:
                adjusted = DateHelper.set_date_with_feb_edge_case(
                    bday, today_date.year + 1
                )

            return adjusted

        return sorted(records, key=lambda r: next_birthday_date(r) or date.max)

    def search(self, query: str) -> list[Record]:
        if query is None:
            raise InvalidException("Search query cannot be None")

        query = query.strip()
        if not query:
            raise InvalidException("Search query cannot be empty")

        tokens = [t.lower() for t in query.split() if t]

        def is_match(record: Record) -> bool:
            haystack = " ".join(self._iter_search_strings(record)).lower()
            return all(token in haystack for token in tokens)

        return self.storage.filter(is_match)

    @staticmethod
    def _iter_search_strings(obj) -> list[str]:
        from dal.entities.Field import Field
        from datetime import date, datetime

        results: list[str] = []
        visited: set[int] = set()

        def walk(o):
            oid = id(o)
            if oid in visited:
                return
            visited.add(oid)

            if o is None:
                return

            if isinstance(o, Field):
                try:
                    results.append(str(o))
                except Exception:
                    pass
                return

            if isinstance(o, (str, int, float, bool, date, datetime)):
                results.append(str(o))
                return

            if isinstance(o, (list, tuple, set, frozenset)):
                for item in o:
                    walk(item)
                return

            if isinstance(o, dict):
                for k, v in o.items():
                    walk(k)
                    walk(v)
                return

            if hasattr(o, "value") and not isinstance(o, (bytes, bytearray)):
                try:
                    results.append(str(getattr(o, "value")))
                except Exception:
                    pass

            try:
                for attr in vars(o).values():
                    walk(attr)
            except Exception:
                pass

            try:
                results.append(str(o))
            except Exception:
                pass

        walk(obj)
        return results

    @staticmethod
    def _validate_record_name(record_name: str) -> None:
        if record_name is None:
            raise InvalidException("Record name cannot be None")

        if not isinstance(record_name, str):
            raise InvalidException("Record name has invalid type")

    @staticmethod
    def _validate_record(record: Record) -> None:
        if record is None:
            raise NotFoundException("Record cannot be None")

        if not isinstance(record, Record):
            raise InvalidException("Record has invalid type")
