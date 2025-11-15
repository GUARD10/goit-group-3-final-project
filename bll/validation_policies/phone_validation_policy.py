import re
from typing import Dict, Pattern


class PhoneValidationPolicy:
    _region: str = "UA"

    _PATTERNS: Dict[str, Pattern[str]] = {
        # Ukraine: +380XX XXX XX XX or 0XX XXX XX XX
        "UA": re.compile(
            r"^(?:\+380|380|0)(?:[ \-]?\d{2})(?:[ \-]?\d{3})(?:[ \-]?\d{2})(?:[ \-]?\d{2})$"
        ),
        # United States: optional +1/1, separators and parentheses
        "US": re.compile(r"^(?:\+?1[ \-]?)?(?:\(?\d{3}\)?[ \-]?)?\d{3}[ \-]?\d{4}$"),
        # International fallback (E.164 core): + and 7-15 digits
        "INTL": re.compile(r"^\+?[1-9]\d{6,14}$"),
    }

    _MESSAGES: Dict[str, str] = {
        "UA": (
            "Use +380XX XXX XX XX or 0XX XXX XX XX; spaces/- allowed; "
            "optional parentheses around operator code."
        ),
        "US": "Use +1 NNN NNN NNNN or (NNN) NNN-NNNN; spaces/- allowed.",
        "INTL": (
            "Use E.164: +[country][number], total 7-15 digits without separators."
        ),
    }

    @classmethod
    def set_region(cls, region: str) -> None:
        key = (region or "").upper()
        if key not in cls._PATTERNS:
            allowed = ", ".join(cls._PATTERNS.keys())
            raise ValueError(f"Unknown phone region: '{region}'. Allowed: {allowed}")
        cls._region = key

    @classmethod
    def get_region(cls) -> str:
        return cls._region

    @classmethod
    def validate(cls, value: str) -> bool:
        return bool(cls._PATTERNS[cls._region].match(value))

    @classmethod
    def error_message(cls, value: str) -> str:
        hint = cls._MESSAGES.get(cls._region, "")
        return f"Invalid {cls._region} phone number: '{value}'. {hint}"
