import os
from pathlib import Path
from typing import Optional


class Config:
    _ALLOWED_PHONE_REGIONS = {"UA", "US", "INTL"}

    def __init__(self) -> None:
        self._contacts_dir: Optional[Path] = None
        self._notes_dir: Optional[Path] = None
        self._backend: Optional[str] = None
        self._phone_region: Optional[str] = None

    @property
    def contacts_dir(self) -> Path:
        if self._contacts_dir is None:
            env_value = os.getenv("ASSISTANT_CONTACTS_DIR")
            self._contacts_dir = (
                Path(env_value) if env_value else Path("files/contacts")
            )
        return self._contacts_dir

    @property
    def notes_dir(self) -> Path:
        if self._notes_dir is None:
            env_value = os.getenv("ASSISTANT_NOTES_DIR")
            self._notes_dir = Path(env_value) if env_value else Path("files/notes")
        return self._notes_dir

    @property
    def backend(self) -> str:
        if self._backend is None:
            value = (os.getenv("ASSISTANT_BACKEND") or "pickle").strip().lower()
            self._backend = value if value in {"pickle", "json"} else "pickle"
        return self._backend

    @property
    def phone_region(self) -> str:
        if self._phone_region is None:
            raw = (os.getenv("ASSISTANT_PHONE_REGION") or "UA").strip().upper()
            self._phone_region = raw if raw in self._ALLOWED_PHONE_REGIONS else "UA"
        return self._phone_region

    def set_contacts_dir(self, path: Path) -> None:
        self._contacts_dir = path

    def set_notes_dir(self, path: Path) -> None:
        self._notes_dir = path


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    global _config
    _config = None
