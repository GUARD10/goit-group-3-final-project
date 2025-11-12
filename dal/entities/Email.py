from dal.entities.Field import Field
import re


class Email(Field):
    # Шаблон:
    #   - дозволяє нормальні символи в локальній частині
    #   - вимагає @
    #   - вимагає домен з крапкою і TLD мінімум 2 літери
    _RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __init__(self, value: str):
        if value is None:
            raise ValueError("Email value cannot be None")

        if not isinstance(value, str):
            raise TypeError(f"Email value should be str not {type(value).__name__}")

        v = value.strip()

        if not v:
            raise ValueError("Email cannot be empty")

        if not self._RE.match(v):
            raise ValueError("Email has invalid format")

        # додаткові перевірки 
        local, domain = v.split("@", 1)

        if ".." in local or ".." in domain:
            raise ValueError("Email cannot contain consecutive dots '..'")

        # обмеження довжини
        if len(v) > 254 or len(local) > 64:
            raise ValueError("Email is too long")

        # нормалізуємо домен у нижній регістр
        normalized = f"{local}@{domain.lower()}"

        super().__init__(normalized)
