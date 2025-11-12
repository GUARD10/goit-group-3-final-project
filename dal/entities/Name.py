from dal.entities.Field import Field


class Name(Field):
    def __init__(self, value: str):
        if value is None:
            raise ValueError("Name value cannot be None")

        if not isinstance(value, str):
            raise TypeError(f"Name value should be str not {type(value).__name__}")

        super().__init__(value)
