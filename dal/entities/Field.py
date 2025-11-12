from typing import Any


class Field:
    def __init__(self, value: Any):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        if not isinstance(other, Field):
            return NotImplemented
        return self.value == other.value
