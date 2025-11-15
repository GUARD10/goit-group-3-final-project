from __future__ import annotations

from datetime import date, datetime
from typing import Any

from dal.entities.field import Field
from dal.exceptions.invalid_error import InvalidError


class SearchHelper:
    """Utility helpers for free-text search across arbitrary entities."""

    @staticmethod
    def prepare_tokens(query: str) -> list[str]:
        if query is None:
            raise InvalidError("Search query cannot be None")

        tokens = [t.lower() for t in query.strip().split() if t]

        if not tokens:
            raise InvalidError("Search query cannot be empty")

        return tokens

    @staticmethod
    def match_all_tokens(obj: Any, tokens: list[str]) -> bool:
        if not tokens:
            return False

        haystack = " ".join(SearchHelper.collect_strings(obj)).lower()
        return all(token in haystack for token in tokens)

    @staticmethod
    def collect_strings(obj: Any) -> list[str]:
        results: list[str] = []
        visited: set[int] = set()

        def walk(value: Any) -> None:
            obj_id = id(value)
            if obj_id in visited:
                return
            visited.add(obj_id)

            if value is None:
                return

            if isinstance(value, Field):
                try:
                    results.append(str(value))
                except Exception:
                    pass
                return

            if isinstance(value, (str, int, float, bool, date, datetime)):
                results.append(str(value))
                return

            if isinstance(value, (list, tuple, set, frozenset)):
                for item in value:
                    walk(item)
                return

            if isinstance(value, dict):
                for key, item in value.items():
                    walk(key)
                    walk(item)
                return

            if hasattr(value, "value") and not isinstance(value, (bytes, bytearray)):
                try:
                    results.append(str(getattr(value, "value")))
                except Exception:
                    pass

            try:
                for attr in vars(value).values():
                    walk(attr)
            except Exception:
                pass

            try:
                results.append(str(value))
            except Exception:
                pass

        walk(obj)
        return results









