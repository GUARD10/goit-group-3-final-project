"""JSON file manager implementation."""
from pathlib import Path
import json
from datetime import datetime, date
from typing import Any

from dal.file_managers.IFileManager import IFileManager
from dal.entities.Record import Record
from dal.entities.Note import Note
from dal.entities.Tag import Tag


class JsonFileManager[Data](IFileManager[Data]):
    """File manager that stores data in JSON format.

    Supports serialization of Record and Note entities with proper
    handling of nested fields (Phone, Birthday, Tag, etc.).
    """

    def __init__(self, base_dir: Path):
        """Initialize JSON file manager.

        Args:
            base_dir: Base directory for storing JSON files
        """
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: Data, name: str) -> None:
        """Save data to JSON file.

        Args:
            data: Data to save (typically dict[str, Record] or dict[str, Note])
            name: Base filename (without extension)
        """
        filename = str(name)
        filepath = self._generate_unique_filename(filename)

        # Serialize data to JSON-compatible format
        json_data = self._serialize(data)

        with filepath.open("w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)

    def load(self, name: str) -> Data:
        """Load data from JSON file.

        Args:
            name: Filename (with or without .json extension)

        Returns:
            Deserialized data

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = self._normalize_name(name)
        if not filepath.exists():
            raise FileNotFoundError(f"File '{filepath}' not found")

        with filepath.open("r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Deserialize from JSON to entities
        return self._deserialize(json_data)

    def delete(self, name: str) -> None:
        """Delete JSON file.

        Args:
            name: Filename to delete
        """
        filepath = self._normalize_name(name)
        if filepath.exists():
            filepath.unlink()

    def get_all_names(self) -> list[str]:
        """Get all JSON filenames in directory.

        Returns:
            List of filenames (including .json extension)
        """
        return [
            f.name
            for f in self.base_dir.iterdir()
            if f.is_file() and f.suffix == ".json"
        ]

    def has_file_with_name(self, name: str) -> bool:
        """Check if file exists.

        Args:
            name: Filename to check

        Returns:
            True if file exists
        """
        return self._normalize_name(name).exists()

    def _normalize_name(self, name: str) -> Path:
        """Normalize filename to include .json extension."""
        name_path = Path(name)
        if name_path.suffix != ".json":
            name_path = name_path.with_suffix(".json")
        return self.base_dir / name_path.name

    def _generate_unique_filename(self, name: str) -> Path:
        """Generate unique filename if file already exists."""
        base_path = self._normalize_name(name)
        if not base_path.exists():
            return base_path

        base = base_path.stem
        ext = base_path.suffix

        counter = 1
        while True:
            new_name = self.base_dir / f"{base}_{counter}{ext}"
            if not new_name.exists():
                return new_name
            counter += 1

    def _serialize(self, data: Any) -> Any:
        """Serialize data to JSON-compatible format.

        Handles Record, Note, and nested field objects.
        """
        if isinstance(data, dict):
            # For storage dictionaries like dict[str, Record]
            return {key: self._serialize(value) for key, value in data.items()}

        if isinstance(data, Record):
            return {
                "_type": "Record",
                "name": data.name.value,
                "phones": [p.value for p in data.phones],
                "emails": [e.value for e in data.emails],
                "birthday": data.birthday.value.isoformat() if data.birthday else None,
                "address": data.address.value if data.address else None,
            }

        if isinstance(data, Note):
            return {
                "_type": "Note",
                "name": data.name.value,
                "title": data.title.value,
                "content": data.content.value,
                "created_at": data.created_at.isoformat(),
                "updated_at": data.updated_at.isoformat() if data.updated_at else None,
                "tags": [
                    {"value": tag.value, "color": tag.color}
                    for tag in data.tags
                ],
            }

        if isinstance(data, (datetime, date)):
            return data.isoformat()

        if isinstance(data, list):
            return [self._serialize(item) for item in data]

        return data

    def _deserialize(self, data: Any) -> Any:
        """Deserialize JSON data back to entities."""
        if isinstance(data, dict):
            # Check if it's a serialized entity
            if "_type" in data:
                if data["_type"] == "Record":
                    # Convert ISO birthday string back to date object
                    birthday_value = None
                    if data.get("birthday"):
                        birthday_value = date.fromisoformat(data["birthday"])

                    # Build Record with proper argument order
                    phones = data.get("phones", [])
                    record = Record(
                        data["name"],  # name is first positional arg
                        *phones,  # phones are varargs
                        emails=data.get("emails"),
                        birthday=birthday_value,
                        address=data.get("address"),
                    )
                    return record

                if data["_type"] == "Note":
                    note = Note(
                        name=data["name"],
                        title=data["title"],
                        content=data["content"],
                        tags=[
                            Tag(tag_data["value"], tag_data["color"])
                            for tag_data in data.get("tags", [])
                        ],
                    )
                    # Restore timestamps
                    note.created_at = datetime.fromisoformat(data["created_at"])
                    if data.get("updated_at"):
                        note.updated_at = datetime.fromisoformat(data["updated_at"])
                    return note

            # Regular dictionary - recurse
            return {key: self._deserialize(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self._deserialize(item) for item in data]

        return data

