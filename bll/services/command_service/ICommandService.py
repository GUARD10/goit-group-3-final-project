from abc import ABC, abstractmethod

from dal.entities.Command import Command


class ICommandService(ABC):
    @abstractmethod
    def add_contact(self, arguments: list) -> str:
        pass

    @abstractmethod
    def add_phone(self, arguments: list) -> str:
        pass

    @abstractmethod
    def show_phone(self, arguments: list) -> str:
        pass

    @abstractmethod
    def show_all(self) -> str:
        pass

    @abstractmethod
    def hello(self) -> str:
        pass

    @abstractmethod
    def help_command(self) -> str:
        pass

    @abstractmethod
    def exit_bot(self) -> None:
        pass

    @abstractmethod
    def get_command(self, command_name: str) -> Command | None:
        pass
