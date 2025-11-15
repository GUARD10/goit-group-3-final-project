from typing import List, Tuple

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog

from bll.services.input_service.i_input_service import IInputService
from dal.exceptions.invalid_error import InvalidError


class InputService(IInputService):
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

        dialog = radiolist_dialog(title=title, text=text, values=options)
        return dialog.run()

    def choose_multiple_from_list(
        self, title: str, text: str, options: list[tuple[str, str]]
    ) -> list[str] | None:
        if not options:
            return []

        dialog = checkboxlist_dialog(title=title, text=text, values=options)
        result = dialog.run()
        if result is None:
            return []
        return [value for value in result]









