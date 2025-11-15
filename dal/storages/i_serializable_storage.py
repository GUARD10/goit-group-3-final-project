from abc import ABC, abstractmethod


class ISerializableStorage[Dict](ABC):
    @abstractmethod
    def export_state(self) -> Dict:
        pass

    @abstractmethod
    def import_state(self, state: Dict) -> None:
        pass
