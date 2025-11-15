from datetime import date, datetime

from dal.entities.field import Field
from dal.exceptions.invalid_error import InvalidError


class Birthday(Field):
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, value: str | datetime | date):
        if isinstance(value, datetime):
            value = value.date()

        elif isinstance(value, date):
            pass

        elif isinstance(value, str):
            try:
                value = datetime.strptime(value, self.DATE_FORMAT).date()
            except ValueError:
                raise InvalidError(
                    f"Birthday must be in format {self.DATE_FORMAT}. "
                    f"Example: {date.today().strftime(self.DATE_FORMAT)}"
                )
        else:
            type_name = type(value).__name__
            raise ValueError(
                f"Birthday value must be str, datetime, or date, not {type_name}"
            )

        if value > date.today():
            raise ValueError("Birthday cannot be in the future")

        super().__init__(value)

    def __str__(self):
        return self.value.strftime(self.DATE_FORMAT)
