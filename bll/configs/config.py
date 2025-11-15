"""Configuration loader for Assistant Bot.

Loads configuration from environment variables with sensible defaults.
Supports customization of file storage paths for multi-user deployments.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration with environment variable support."""

    def __init__(self):
        """Initialize configuration from environment variables or defaults."""
        self._contacts_dir: Optional[Path] = None
        self._notes_dir: Optional[Path] = None
        self._backend: Optional[str] = None

    @property
    def contacts_dir(self) -> Path:
        """Get contacts storage directory.

        Can be customized via ASSISTANT_CONTACTS_DIR environment variable.
        Default: files/contacts
        """
        if self._contacts_dir is None:
            env_value = os.getenv("ASSISTANT_CONTACTS_DIR")
            self._contacts_dir = Path(env_value) if env_value else Path("files/contacts")
        return self._contacts_dir

    @property
    def notes_dir(self) -> Path:
        """Get notes storage directory.

        Can be customized via ASSISTANT_NOTES_DIR environment variable.
        Default: files/notes
        """
        if self._notes_dir is None:
            env_value = os.getenv("ASSISTANT_NOTES_DIR")
            self._notes_dir = Path(env_value) if env_value else Path("files/notes")
        return self._notes_dir

    @property
    def backend(self) -> str:
        """Selected persistence backend (pickle|json). Default is 'pickle'."""
        if self._backend is None:
            value = (os.getenv("ASSISTANT_BACKEND") or "pickle").strip().lower()
            self._backend = value if value in {"pickle", "json"} else "pickle"
        return self._backend

    def set_contacts_dir(self, path: Path) -> None:
        """Override contacts directory programmatically (useful for testing)."""
        self._contacts_dir = path

    def set_notes_dir(self, path: Path) -> None:
        """Override notes directory programmatically (useful for testing)."""
        self._notes_dir = path

    def set_backend(self, backend: str) -> None:
        """Override backend programmatically (useful for testing)."""
        backend = (backend or "").strip().lower()
        self._backend = backend if backend in {"pickle", "json"} else "pickle"


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance (singleton pattern)."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset configuration (mainly for testing purposes)."""
    global _config
    _config = None
