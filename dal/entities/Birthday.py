from datetime import datetime, date

from dal.entities.Field import Field
from dal.exceptions.InvalidException import InvalidException


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
                raise InvalidException(
                    f"Birthday must be in format {self.DATE_FORMAT}. "
                    f"Example: {date.today().strftime(self.DATE_FORMAT)}"
                )
        else:
            raise InvalidException(
                f"Birthday value must be str, datetime, or date, not {type(value).__name__}"
            )

        if value > date.today():
            raise InvalidException("Birthday cannot be in the future")

        super().__init__(value)

    def __str__(self):
        return self.value.strftime(self.DATE_FORMAT)