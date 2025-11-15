from bll.registries.IRegistry import IRegistry
from bll.services.file_service.IFileService import IFileService


class FileServiceRegistry(IRegistry):
    def __init__(self, contact_file_service, note_file_service):
        self._services = {
            "contacts": contact_file_service,
            "notes": note_file_service,
        }

    def get(self, key: str) -> IFileService:
        key = key.lower().strip()

        if key not in self._services:
            raise ValueError(f"Unknown file service '{key}'")

        return self._services[key]

    def get_all(self) -> dict[str, IFileService]:
        return self._services
