from abc import ABC, abstractmethod


class ISerializableStorage[State](ABC):
    @abstractmethod
    def export_state(self) -> State:
        pass

    @abstractmethod
    def import_state(self, state: State) -> None:
        pass
