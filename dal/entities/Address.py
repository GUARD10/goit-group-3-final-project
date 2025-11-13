from dal.entities.Field import Field


class Address(Field):
    def __init__(self, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError("Address cannot be empty")
        super().__init__(value)
