from abc import ABC, abstractmethod


class IInputService(ABC):
    @abstractmethod
    def handle(self, user_input: str) -> str:
        pass
