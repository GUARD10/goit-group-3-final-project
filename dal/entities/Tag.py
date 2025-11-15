from dal.entities.field import Field


class Tag(Field):
    def __init__(self, value: str, color: str | None = None):
        if not isinstance(value, str):
            raise TypeError(f"Tag value should be str not {type(value).__name__}")

        value = value.strip()
        if not value:
            raise ValueError("Tag value cannot be empty")

        super().__init__(value)

        if color is not None and not isinstance(color, str):
            raise TypeError(f"Tag color should be str not {type(color).__name__}")

        if isinstance(color, str):
            color = color.strip()
            self.color = color or None
        else:
            self.color = None

    def __str__(self):
        return f"{self.value} ({self.color})" if self.color else self.value

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return super().__eq__(other)
        return self.value == other.value and self.color == other.color

    def __hash__(self) -> int:
        return hash((self.value, self.color))









