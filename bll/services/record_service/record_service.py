from datetime import date

from bll.helpers.date_helper import DateHelper
from bll.helpers.search_helper import SearchHelper
from bll.services.record_service.i_record_service import IRecordService
from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError
from dal.storages.i_storage import IStorage


class RecordService(IRecordService):
    def __init__(self, storage: IStorage[str, Record]):
        self.storage = storage

    def save(self, new_record: Record) -> Record:
        self._validate_record(new_record)

        if self.has(new_record.name.value):
            raise AlreadyExistsError(f"Record '{new_record.name}' already exists")

        self.storage.add(new_record)

        return new_record

    def update(self, record_name: str, new_record: Record) -> Record:
        self._validate_record(new_record)

        if not self.has(record_name):
            raise NotFoundError(f"Record '{record_name}' not found")

        self.storage.update_item(record_name, new_record)

        return new_record

    def get_by_name(self, record_name: str) -> Record:
        record = self.storage.find(record_name)

        if not record:
            raise NotFoundError(f"Record '{record_name}' not found")

        return record

    def get_all(self) -> list[Record]:
        return self.storage.all_values()

    def rename(self, record_name: str, new_name: str) -> Record:
        if not self.has(record_name):
            raise NotFoundError(f"Record '{record_name}' not found")

        record = self.get_by_name(record_name)
        record.name.value = new_name

        self.delete(record_name)
        self.save(record)

        return record

    def delete(self, record_name: str) -> None:
        if not self.has(record_name):
            raise NotFoundError(f"Record '{record_name}' not found")

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
        tokens = SearchHelper.prepare_tokens(query)

        def is_match(record: Record) -> bool:
            return SearchHelper.match_all_tokens(record, tokens)

        return self.storage.filter(is_match)

    def _validate_record_arguments(self, record_name: str, record_phone: str) -> None:
        self._validate_record_name(record_name)

        if not isinstance(record_phone, str):
            raise TypeError("Phone value should be str")

        if not record_phone or not record_phone.strip():
            raise ValueError("Phone value cannot be empty")

        if not PhoneValidationPolicy.validate(record_phone):
            PhoneValidationPolicy.error_message(record_phone)

    @staticmethod
    def _validate_record_name(record_name: str) -> None:
        if record_name is None:
            raise InvalidError("Record name cannot be None")

        if not isinstance(record_name, str):
            raise InvalidError("Record name has invalid type")

    @staticmethod
    def _validate_record(record: Record) -> None:
        if record is None:
            raise NotFoundError("Record cannot be None")

        if not isinstance(record, Record):
            raise InvalidError("Record has invalid type")
