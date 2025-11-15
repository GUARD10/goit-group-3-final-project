import re

from dal.entities.field import Field


class Phone(Field):
    PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Phone value should be str not {type(value).__name__}")

        if not self.PHONE_PATTERN.match(value):
            raise ValueError(f"Incorrect phone number: '{value}'")

        super().__init__(value)









