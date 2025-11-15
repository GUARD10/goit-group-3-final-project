import re
from typing import List, Tuple

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

from bll.services.input_service.i_input_service import IInputService
from dal.exceptions.invalid_error import InvalidError


class _DropdownCompleter(Completer):
    def __init__(self, options: list[tuple[str, str, str]]):
        self._options = options

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        normalized = text.strip().lower()
        for value, display, style in self._options:
            if normalized and not value.lower().startswith(normalized):
                continue
            yield Completion(
                value,
                start_position=-len(text),
                display=display,
                style=style,
            )


class InputService(IInputService):
    _COLOR_RE = re.compile(r"(#(?:[0-9a-fA-F]{6}))")

    def handle(self, user_input: str) -> Tuple[str, List[str]]:
        return self._parse_input(user_input)

    @staticmethod
    def _parse_input(user_input: str) -> Tuple[str, List[str]]:
        parts = user_input.split()
        if not parts:
            raise InvalidError("Empty input")

        command = parts[0].lower()
        arguments = parts[1:]
        return command, arguments

    def read_value(
        self,
        label: str,
        *,
        default: str | None = None,
        allow_empty: bool = False,
    ) -> str | None:
        while True:
            if default is None:
                value = prompt(f"{label}: ").strip()
            else:
                value = prompt(f"{label}: ", default=default).strip()

            if value == "/cancel":
                return None

            if not value and not allow_empty:
                print("❌ Value cannot be empty. Please try again.")
                continue

            return value

    def read_multiline(
        self,
        header: str,
        *,
        min_len: int = 10,
        show_existing: str | None = None,
    ) -> str | None:
        print(header)

        if show_existing is not None:
            print("Current content:")
            print("--------------------")
            print(show_existing)
            print("--------------------")

        lines: list[str] = []

        while True:
            line = prompt("> ").strip()

            if line == "/cancel":
                return None

            if line == "":
                if not lines:
                    print(
                        "❌ Content cannot be empty. "
                        "Enter at least one line or type /cancel."
                    )
                    continue
                break

            lines.append(line)

        result = "\n".join(lines)

        if len(result) < min_len:
            print(f"❌ Content is too short (min {min_len} characters).")
            return None

        return result

    def choose_from_list(
        self, title: str, text: str, options: list[tuple[str, str]]
    ) -> str | None:
        if not options:
            return None

        print(f"\n{title}")
        if text:
            print(text)
        print("Press Enter to cancel or type /cancel.")

        completer = _DropdownCompleter(self._prepare_dropdown_options(options))
        valid_values = {value for value, _ in options}

        while True:
            raw = prompt(
                "Choice: ",
                completer=completer,
                complete_while_typing=True,
            ).strip()

            if raw == "" or raw == "/cancel":
                return None

            if raw not in valid_values:
                print("❌ Please pick one of the suggested options.")
                continue

            return raw

    def choose_multiple_from_list(
        self,
        title: str,
        text: str,
        options: list[tuple[str, str]],
        *,
        allow_custom: bool = False,
    ) -> list[str] | None:
        if not options and not allow_custom:
            return []

        print(f"\n{title}")
        if text:
            print(text)
        print("Press Enter to finish, /cancel to abort.")

        completer = _DropdownCompleter(self._prepare_dropdown_options(options))
        valid_values = {value for value, _ in options}

        selected: list[str] = []

        while True:
            raw = prompt(
                f"Tag #{len(selected) + 1}: ",
                completer=completer,
                complete_while_typing=True,
            ).strip()

            if raw == "/cancel":
                return []

            if raw == "":
                break

            if raw not in valid_values:
                if not allow_custom:
                    print("❌ Please use one of the suggested options.")
                    continue
            else:
                value = raw
                if value in selected:
                    print("⚠️ Option already selected.")
                    continue
                selected.append(value)
                continue

            if raw in selected:
                print("⚠️ Value already added.")
                continue

            selected.append(raw)

        return selected

    def _prepare_dropdown_options(
        self, options: list[tuple[str, str]]
    ) -> list[tuple[str, str, str]]:
        prepared: list[tuple[str, str, str]] = []
        for value, label in options:
            style = ""
            hex_color = self._extract_hex_color(label)
            if hex_color:
                style = f"fg:{hex_color} bold"
            prepared.append((value, label, style))
        return prepared

    def _extract_hex_color(self, label: str) -> str | None:
        match = self._COLOR_RE.search(label)
        if match:
            return match.group(1)
        return None
