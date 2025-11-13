from dal.entities.Birthday import Birthday
from dal.entities.Name import Name
from dal.entities.Phone import Phone
from dal.entities.Email import Email
from dal.entities.Address import Address
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException
from datetime import datetime, date


class Record:
    def __init__(
        self,
        name: str,
        *phone_numbers: str,
        emails: list[str] | None = None,
        birthday: str | datetime | date | None = None,
        address: str | None = None,
    ):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.emails: list[Phone] = []
        self.birthday: Birthday | None = None
        self.address: Address | None = None

        if birthday is not None:
            self.birthday = Birthday(birthday)

        for phone_number in phone_numbers:
            self.phones.append(Phone(phone_number))

        if emails is not None:
            for email in emails:
                self.emails.append(Email(email))

        if address is not None:
            self.address = Address(address)

    def __str__(self):
        phones_str = ", ".join(p.value for p in self.phones) if self.phones else "—"
        emails_str = ", ".join(e.value for e in self.emails) if self.emails else "—"
        birthday_str = self.birthday.value if self.birthday else "—"
        address_str = self.address.value if self.address else "—"

        return (
            f"\nContact:"
            f"\nName: {self.name.value}"
            f"\nPhones: {phones_str}"
            f"\nEmails: {emails_str}"
            f"\nBirthday: {birthday_str}"
            f"\nAddress: {address_str}\n"
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

    def has_email(self, email: str | Email) -> bool:
        return email in self.emails

    def find_email(self, email: str | Email) -> Email | None:
        if not self.has_email(email):
            raise NotFoundException(f"Record {self.name} do not have {email} box")

        return next((e for e in self.emails if e == email), None)

    def update(self):
        from dal.entity_builders.record_builder.RecordBuilder import RecordBuilder

        return RecordBuilder(self)
