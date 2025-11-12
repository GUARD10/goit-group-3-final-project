from datetime import datetime, date
from typing import Union

from dal.entities.Record import Record
from dal.entities.Name import Name
from dal.entities.Phone import Phone
from dal.entities.Birthday import Birthday
from dal.Exceptions.InvalidException import InvalidException
from dal.Exceptions.AlreadyExistException import AlreadyExistException
from dal.Exceptions.NotFoundException import NotFoundException
from bll.helpers.DateHelper import DateHelper


class RecordBuilder:
    def __init__(self, record: Record):
        self._record = record

    def set_name(self, name: str) -> "RecordBuilder":
        if not name or not name.strip():
            raise InvalidException("Name cannot be empty")
        self._record.name = Name(name.strip())
        return self

    def build(self) -> Record:
        if not self._record.name or not self._record.name.value.strip():
            raise InvalidException("Record must have a name before building")
        return self._record

    def add_phone(self, phone: str | Phone) -> "RecordBuilder":
        if self._record.has_phone(phone):
            raise AlreadyExistException(f"Record {self._record.name} already has phone {phone}")

        phone_obj = phone if isinstance(phone, Phone) else Phone(phone)
        self._record.phones.append(phone_obj)
        return self

    def update_phone(self, old_phone: str | Phone, new_phone: str | Phone) -> "RecordBuilder":
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
        return self

    def remove_phone(self, phone: str | Phone) -> "RecordBuilder":
        if not self._record.has_phone(phone):
            raise NotFoundException(f"Record {self._record.name} does not have phone {phone}")

        phone_value = phone.value if isinstance(phone, Phone) else str(phone)
        self._record.phones = [p for p in self._record.phones if p.value != phone_value]
        return self

    def clear_phones(self) -> "RecordBuilder":
        self._record.phones.clear()
        return self

    def set_birthday(self, birthday: Union[str, datetime, date]) -> "RecordBuilder":
        birthday_value = DateHelper.parse_to_date(birthday)
        self._record.birthday = Birthday(birthday_value)
        return self

    def clear_birthday(self) -> "RecordBuilder":
        self._record.birthday = None
        return self
