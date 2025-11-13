from abc import ABC, abstractmethod
from typing import Tuple, List


class IInputService(ABC):
    @abstractmethod
    def handle(self, user_input: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def read_value(
        self,
        label: str,
        *,
        default: str | None = None,
        allow_empty: bool = False,
    ) -> str | None:
        pass

    @abstractmethod
    def read_multiline(
        self,
        header: str,
        *,
        min_len: int = 10,
        show_existing: str | None = None,
    ) -> str | None:
        pass
