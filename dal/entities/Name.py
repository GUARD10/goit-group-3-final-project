from dal.entities.field import Field


class Name(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Name value should be str not {type(value).__name__}")

        if value is None or not value.strip():
            raise ValueError("Name value cannot be empty")

        super().__init__(value)
