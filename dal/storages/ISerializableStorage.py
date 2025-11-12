from abc import ABC, abstractmethod


class ISerializableStorage[Data](ABC):
    @abstractmethod
    def export_state(self) -> Data:
        pass

    @abstractmethod
    def import_state(self, state: Data) -> None:
        pass
