import inspect

from bll.services.command_service.ICommandService import ICommandService
from bll.services.input_service.IInputService import IInputService
from dal.exceptions.InvalidException import InvalidException

class InputService(IInputService):
    def __init__(self, command_service: ICommandService):
        self.command_service = command_service

    def handle(self, user_input: str) -> str:
        command_name, arguments = self._parse_input(user_input)

        command = self.command_service.get_command(command_name)

        if not command:
            raise InvalidException('Invalid command')

        handler = command.handler

        sig = inspect.signature(handler)
        param_count = len(sig.parameters)

        return handler() if param_count == 0 else handler(arguments)

    @staticmethod
    def _parse_input(user_input: str) -> tuple[str, list]:
        parts = user_input.split()
        command = parts[0].lower()
        arguments = parts[1:]
        return command, arguments