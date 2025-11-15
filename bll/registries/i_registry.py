from abc import ABC, abstractmethod


class IRegistry(ABC):
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def get_all(self):
        pass
