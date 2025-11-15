"""Tests for JSON file manager."""
import json
from pathlib import Path
from datetime import datetime, date
import pytest

from dal.file_managers.json_file_manager.JsonFileManager import JsonFileManager
from dal.entities.Record import Record
from dal.entities.Note import Note
from dal.entities.Tag import Tag


class TestJsonFileManager:
    """Test JSON file manager functionality."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tests."""
        test_dir = tmp_path / "json_test"
        test_dir.mkdir()
        return test_dir

    @pytest.fixture
    def json_manager(self, temp_dir):
        """Create JSON file manager instance."""
        return JsonFileManager[dict[str, Record]](temp_dir)

    def test_save_and_load_records(self, json_manager, temp_dir):
        """Test saving and loading contact records."""
        # Create test data
        records = {
            "john": Record("John Doe", "1234567890", birthday="15.01.1990"),
            "jane": Record("Jane Smith", "0987654321", "1111111111", emails=["jane@test.com"]),
        }

        # Save
        json_manager.save(records, "test_contacts")

        # Verify file exists
        assert (temp_dir / "test_contacts.json").exists()

        # Load
        loaded = json_manager.load("test_contacts")

        # Verify
        assert len(loaded) == 2
        assert "john" in loaded
        assert "jane" in loaded
        assert loaded["john"].name.value == "John Doe"
        assert len(loaded["john"].phones) == 1
        assert loaded["john"].phones[0].value == "1234567890"
        assert loaded["jane"].name.value == "Jane Smith"
        assert len(loaded["jane"].phones) == 2

    def test_save_and_load_notes(self, temp_dir):
        """Test saving and loading notes."""
        manager = JsonFileManager[dict[str, Note]](temp_dir)

        # Create test notes
        notes = {
            "note1": Note(
                "note1",
                "Test Title",
                "Test content here",
                tags=[Tag("work", "#FF0000"), Tag("important", "#00FF00")],
            ),
            "note2": Note("note2", "Another Note", "More content"),
        }

        # Save
        manager.save(notes, "test_notes")

        # Load
        loaded = manager.load("test_notes")

        # Verify
        assert len(loaded) == 2
        assert loaded["note1"].title.value == "Test Title"
        assert loaded["note1"].content.value == "Test content here"
        assert len(loaded["note1"].tags) == 2
        tag_values = {tag.value for tag in loaded["note1"].tags}
        assert "work" in tag_values
        assert "important" in tag_values
        # Check colors are preserved
        tag_dict = {tag.value: tag.color for tag in loaded["note1"].tags}
        assert tag_dict["work"] == "#FF0000"
        assert tag_dict["important"] == "#00FF00"

    def test_birthday_serialization(self, json_manager, temp_dir):
        """Test proper birthday date serialization."""
        records = {
            "test": Record("Test User", birthday=date(1995, 6, 20)),
        }

        json_manager.save(records, "birthday_test")
        loaded = json_manager.load("birthday_test")

        assert loaded["test"].birthday is not None
        assert loaded["test"].birthday.value.year == 1995
        assert loaded["test"].birthday.value.month == 6
        assert loaded["test"].birthday.value.day == 20

    def test_json_file_is_human_readable(self, json_manager, temp_dir):
        """Test that JSON files are properly formatted and readable."""
        records = {
            "test": Record("Test User", "1234567890"),
        }

        json_manager.save(records, "readable_test")

        # Read raw JSON
        with open(temp_dir / "readable_test.json", "r", encoding="utf-8") as f:
            raw_json = f.read()
            json_data = json.loads(raw_json)

        # Verify structure
        assert "test" in json_data
        assert json_data["test"]["_type"] == "Record"
        assert json_data["test"]["name"] == "Test User"
        assert "1234567890" in json_data["test"]["phones"]

    def test_delete_file(self, json_manager, temp_dir):
        """Test file deletion."""
        records = {"test": Record("Test")}
        json_manager.save(records, "to_delete")

        assert json_manager.has_file_with_name("to_delete")
        json_manager.delete("to_delete")
        assert not json_manager.has_file_with_name("to_delete")

    def test_get_all_names(self, json_manager):
        """Test getting all file names."""
        json_manager.save({"a": Record("A")}, "file1")
        json_manager.save({"b": Record("B")}, "file2")
        json_manager.save({"c": Record("C")}, "file3")

        names = json_manager.get_all_names()
        assert len(names) == 3
        assert "file1.json" in names
        assert "file2.json" in names
        assert "file3.json" in names

    def test_unique_filename_generation(self, json_manager):
        """Test that duplicate names get unique filenames."""
        json_manager.save({"a": Record("A")}, "duplicate")
        json_manager.save({"b": Record("B")}, "duplicate")
        json_manager.save({"c": Record("C")}, "duplicate")

        names = json_manager.get_all_names()
        assert "duplicate.json" in names
        assert "duplicate_1.json" in names
        assert "duplicate_2.json" in names

    def test_file_not_found(self, json_manager):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            json_manager.load("nonexistent")

    def test_normalize_name_adds_extension(self, json_manager):
        """Test that filenames without extension get .json added."""
        records = {"test": Record("Test")}
        json_manager.save(records, "no_extension")

        # Should be able to load with or without extension
        loaded1 = json_manager.load("no_extension")
        loaded2 = json_manager.load("no_extension.json")

        assert loaded1["test"].name.value == "Test"
        assert loaded2["test"].name.value == "Test"

    def test_empty_storage(self, json_manager):
        """Test saving and loading empty storage."""
        empty_records = {}
        json_manager.save(empty_records, "empty")

        loaded = json_manager.load("empty")
        assert loaded == {}

    def test_note_timestamps_preserved(self, temp_dir):
        """Test that note timestamps are preserved during save/load."""
        manager = JsonFileManager[dict[str, Note]](temp_dir)

        # Create note with specific timestamps
        note = Note("test", "Title", "Content that is long enough for validation")
        original_created = note.created_at
        note.updated_at = datetime(2025, 11, 15, 10, 30, 0)

        notes = {"test": note}
        manager.save(notes, "timestamp_test")

        # Load and verify
        loaded = manager.load("timestamp_test")
        assert loaded["test"].created_at == original_created
        assert loaded["test"].updated_at == datetime(2025, 11, 15, 10, 30, 0)

    def test_unicode_support(self, json_manager):
        """Test that Unicode characters are properly handled."""
        records = {
            "ukrainian": Record("Тарас Шевченко", "0501234567"),
            "emoji": Record("User 😀", "1234567890"),
        }

        json_manager.save(records, "unicode_test")
        loaded = json_manager.load("unicode_test")

        assert loaded["ukrainian"].name.value == "Тарас Шевченко"
        assert loaded["emoji"].name.value == "User 😀"

    def test_record_with_all_fields(self, json_manager):
        """Test record with all possible fields populated."""
        records = {
            "complete": Record(
                "Complete User",
                "1234567890",
                "0987654321",
                emails=["user@test.com", "user2@test.com"],
                birthday="15.05.1990",
                address="123 Main St, City",
            )
        }

        json_manager.save(records, "complete_test")
        loaded = json_manager.load("complete_test")

        record = loaded["complete"]
        assert record.name.value == "Complete User"
        assert len(record.phones) == 2
        assert len(record.emails) == 2
        assert record.emails[0].value == "user@test.com"
        assert record.birthday is not None
        assert record.address.value == "123 Main St, City"

