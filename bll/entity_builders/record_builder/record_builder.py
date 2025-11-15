from datetime import date, datetime
from typing import Union

from bll.helpers.date_helper import DateHelper
from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy
from dal.entities.address import Address
from dal.entities.birthday import Birthday
from dal.entities.email import Email
from dal.entities.name import Name
from dal.entities.phone import Phone
from dal.entities.record import Record
from dal.exceptions.already_exists_error import AlreadyExistsError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError


class RecordBuilder:
    def __init__(self, record: Record):
        self._record = record

    def set_name(self, name: str) -> "RecordBuilder":
        if not name or not name.strip():
            raise InvalidError("Name cannot be empty")
        self._record.name = Name(name.strip())
        return self

    def build(self) -> Record:
        if not self._record.name or not self._record.name.value.strip():
            raise InvalidError("Record must have a name before building")
        return self._record

    def add_phone(self, phone: str | Phone) -> "RecordBuilder":
        if self._record.has_phone(phone):
            raise AlreadyExistsError(
                f"Record {self._record.name} already has phone {phone}"
            )

        phone_obj = phone if isinstance(phone, Phone) else Phone(phone)

        if not PhoneValidationPolicy.validate(phone_obj.value):
            raise InvalidError(PhoneValidationPolicy.error_message(phone_obj.value))

        self._record.phones.append(phone_obj)
        return self

    def remove_phone(self, phone: str | Phone) -> "RecordBuilder":
        if not self._record.has_phone(phone):
            raise NotFoundError(
                f"Record {self._record.name} does not have phone {phone}"
            )

        phone_value = phone.value if isinstance(phone, Phone) else str(phone)
        self._record.phones = [p for p in self._record.phones if p.value != phone_value]
        return self

    def clear_phones(self) -> "RecordBuilder":
        self._record.phones.clear()
        return self

    def set_birthday(self, birthday: Union[str, datetime, date]) -> "RecordBuilder":
        birthday_value = DateHelper.parse_to_date(birthday)
        try:
            self._record.birthday = Birthday(birthday_value)
            return self
        except ValueError as e:
            raise InvalidError(str(e))

    def clear_birthday(self) -> "RecordBuilder":
        self._record.birthday = None
        return self

    def add_email(self, email: str | Email) -> "RecordBuilder":
        try:
            email_obj = email if isinstance(email, Email) else Email(email)

            if self._record.emails is None:
                self._record.emails = []

            if email_obj in self._record.emails:
                raise AlreadyExistsError(
                    f"Record {self._record.name} already has email {email_obj.value}"
                )

            self._record.emails.append(email_obj)
            return self
        except ValueError as e:
            raise InvalidError(str(e))


    def remove_email(self, email: str | Email) -> "RecordBuilder":
        try:
            email_obj = email if isinstance(email, Email) else Email(email)

            if email_obj not in self._record.emails:
                raise NotFoundError(
                    f"Record {self._record.name} does not have email {email_obj.value}"
                )

            self._record.emails = [e for e in self._record.emails if e != email_obj]
            return self
        except ValueError as e:
            raise InvalidError(str(e))

    def set_address(self, address: str | Address) -> "RecordBuilder":
        try:
            addr_obj = address if isinstance(address, Address) else Address(address)
            self._record.address = addr_obj
            return self
        except ValueError as e:
            raise InvalidError(str(e))

    def clear_address(self) -> "RecordBuilder":
        if self._record.address is None:
            raise NotFoundError(f"Record {self._record.name} does not have address")

        self._record.address = None
        return self









