"""Tests for configuration module."""
import os
from pathlib import Path

from configs.config import Config, get_config, reset_config


class TestConfig:
    """Test configuration loading and environment variable support."""

    def teardown_method(self):
        """Reset config after each test."""
        reset_config()
        # Clean up environment variables
        os.environ.pop("ASSISTANT_CONTACTS_DIR", None)
        os.environ.pop("ASSISTANT_NOTES_DIR", None)

    def test_default_contacts_dir(self):
        """Test default contacts directory."""
        config = Config()
        assert config.contacts_dir == Path("files/contacts")

    def test_default_notes_dir(self):
        """Test default notes directory."""
        config = Config()
        assert config.notes_dir == Path("files/notes")

    def test_env_var_contacts_dir(self):
        """Test contacts directory from environment variable."""
        os.environ["ASSISTANT_CONTACTS_DIR"] = "/custom/contacts"
        config = Config()
        assert config.contacts_dir == Path("/custom/contacts")

    def test_env_var_notes_dir(self):
        """Test notes directory from environment variable."""
        os.environ["ASSISTANT_NOTES_DIR"] = "/custom/notes"
        config = Config()
        assert config.notes_dir == Path("/custom/notes")

    def test_programmatic_override_contacts(self):
        """Test programmatic override of contacts directory."""
        config = Config()
        custom_path = Path("/override/contacts")
        config.set_contacts_dir(custom_path)
        assert config.contacts_dir == custom_path

    def test_programmatic_override_notes(self):
        """Test programmatic override of notes directory."""
        config = Config()
        custom_path = Path("/override/notes")
        config.set_notes_dir(custom_path)
        assert config.notes_dir == custom_path

    def test_singleton_pattern(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reset_config(self):
        """Test that reset_config creates new instance."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2

    def test_env_var_precedence(self):
        """Test that environment variables take precedence over defaults."""
        os.environ["ASSISTANT_CONTACTS_DIR"] = "/env/contacts"
        config = Config()
        # First access reads from env
        assert config.contacts_dir == Path("/env/contacts")
        # Change env var - should not affect already loaded config
        os.environ["ASSISTANT_CONTACTS_DIR"] = "/env/contacts2"
        assert config.contacts_dir == Path("/env/contacts")

    def test_programmatic_override_precedence(self):
        """Test that programmatic override takes precedence over env vars."""
        os.environ["ASSISTANT_CONTACTS_DIR"] = "/env/contacts"
        config = Config()
        override_path = Path("/override/contacts")
        config.set_contacts_dir(override_path)
        assert config.contacts_dir == override_path

