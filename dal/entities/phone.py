from dal.entities.field import Field


class Phone(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Phone value should be str not {type(value).__name__}")

        if not value or not value.strip():
            raise ValueError("Phone value cannot be empty")

        super().__init__(value)
