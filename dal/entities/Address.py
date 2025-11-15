from dal.entities.field import Field


class Address(Field):
    MIN_LEN = 3
    MAX_LEN = 255

    def __init__(self, value: str):
        if value is None:
            raise ValueError("Address value cannot be None")

        if not isinstance(value, str):
            raise TypeError(f"Address value should be str not {type(value).__name__}")

        raw = value.strip()
        if not raw:
            raise ValueError("Address cannot be empty")

        if len(raw) < self.MIN_LEN:
            raise ValueError("Address is too short")
        if len(raw) > self.MAX_LEN:
            raise ValueError("Address is too long")

        if raw.isdigit():
            raise ValueError("Address cannot contain only digits")

        if not any(ch.isalpha() for ch in raw):
            raise ValueError("Address must contain at least one letter")

        # Перевірка на допустимі символи:
        # - літери (будь-які)
        # - цифри
        # - пробіл
        # - базова пунктуація для адрес
        allowed_punct = ",.-/'’#"

        for ch in raw:
            if ch.isalpha() or ch.isdigit() or ch == " " or ch in allowed_punct:
                continue
            raise ValueError(f"Address contains invalid character: {repr(ch)}")

        # Нормалізація пробілів
        normalized = " ".join(raw.split())

        super().__init__(normalized)
