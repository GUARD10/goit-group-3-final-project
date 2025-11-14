from bll.registries.IRegistry import IRegistry
from bll.services.pickle_file_service.IPickleFileService import IPickleFileService


class FileServiceRegistry(IRegistry):
    def __init__(self, contact_file_service, note_file_service):
        self._services = {
            "contacts": contact_file_service,
            "notes": note_file_service,
        }

    def get(self, key: str) -> IPickleFileService:
        key = key.lower().strip()

        if key not in self._services:
            raise ValueError(f"Unknown file service '{key}'")

        return self._services[key]

    def get_all(self) -> dict[str, IPickleFileService]:
        return self._services
