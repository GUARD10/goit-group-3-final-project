from dal.entities.Birthday import Birthday
from dal.entities.Name import Name
from dal.entities.Phone import Phone
from dal.entities.Email import Email
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from datetime import datetime, date


class Record:
    def __init__(
        self,
        name: str,
        *phone_numbers: str,
        email: str | None = None,
        birthday: str | datetime | date | None = None,
    ):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.email: Email | None = None
        self.birthday: Birthday | None = None

        if birthday is not None:
            self.birthday = Birthday(birthday)

        for phone_number in phone_numbers:
            self.phones.append(Phone(phone_number))

        if email is not None:
            self.email = Email(email)

    def __str__(self):
        return (
            f"\nContact: \nName: {self.name.value}, \nPhones: {', '.join(p.value for p in self.phones)}"
            + (f", \nEmail: {self.email.value}" if self.email else "")
            + (f", \nBirthday: {self.birthday.value}" if self.birthday else "")
        )

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name.value == other
        if not isinstance(other, Record):
            return NotImplemented
        return self.name == other.name and self.phones == other.phones

    def has_phone(self, phone: str | Phone) -> bool:
        if not phone:
            raise InvalidException("Phone cannot be None")

        return phone in self.phones

    def find_phone(self, phone: str | Phone) -> Phone | None:
        if not self.has_phone(phone):
            raise NotFoundException(f"Record {self.name} do not have {phone} phone")

        return next((p for p in self.phones if p == phone), None)

    def update(self):
        from dal.entity_builders.record_builder.RecordBuilder import RecordBuilder

        return RecordBuilder(self)
