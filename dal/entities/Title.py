from dal.entities.Field import Field


class Title(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Title value should be str not {type(value).__name__}")

        if not value or not value.strip():
            raise ValueError("Title value cannot be empty")

        super().__init__(value)
