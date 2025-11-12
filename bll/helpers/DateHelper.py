from datetime import datetime, date, timedelta
from typing import Union, Optional

from dal.exceptions.InvalidException import InvalidException


class DateHelper:
    @staticmethod
    def is_date_within_next_week(
        event_date: Union[str, datetime, date, None],
        today: Optional[Union[str, datetime, date]] = None,
    ) -> bool:
        if event_date is None:
            return False

        today_date = DateHelper.parse_to_date(today or date.today())
        event_date_parsed = DateHelper.parse_to_date(event_date)
        next_week = today_date + timedelta(days=7)

        adjusted_date = DateHelper.set_date_with_feb_edge_case(
            event_date_parsed, today_date.year
        )

        if adjusted_date.weekday() == 5:  # Saturday
            adjusted_date += timedelta(days=2)
        elif adjusted_date.weekday() == 6:  # Sunday
            adjusted_date += timedelta(days=1)

        return today_date <= adjusted_date <= next_week

    @staticmethod
    def parse_to_date(value: Union[str, datetime, date]) -> date:
        if not value:
            raise InvalidException("Value cannot be None")
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y.%m.%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            raise InvalidException(f"Unrecognized date format: {value!r}")
        raise InvalidException(f"Unsupported date type: {type(value).__name__}")

    @staticmethod
    def set_date_with_feb_edge_case(birthday_date: date, target_year: int) -> date:
        is_leap = target_year % 4 == 0 and (
            target_year % 100 != 0 or target_year % 400 == 0
        )

        if birthday_date.month == 2 and birthday_date.day == 29 and not is_leap:
            return date(target_year, 2, 28)

        return date(target_year, birthday_date.month, birthday_date.day)
