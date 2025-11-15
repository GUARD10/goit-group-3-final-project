from dal.entities.field import Field


class Content(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Content value should be str not {type(value).__name__}")

        if not value or len(value.strip()) < 10:
            raise ValueError("Content value must be at least 10 characters long")

        super().__init__(value)









