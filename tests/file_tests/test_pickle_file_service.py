from unittest.mock import MagicMock

import pytest

from bll.services.file_service.file_service import FileService
from dal.exceptions.invalid_error import InvalidError


@pytest.fixture
def mock_file_manager():
    fm = MagicMock()
    fm.get_all_names.return_value = ["file1.pkl", "file2.pkl"]
    return fm


@pytest.fixture
def mock_storage():
    st = MagicMock()
    st.export_state.return_value = {"a": 1}
    return st


@pytest.fixture
def service(mock_file_manager, mock_storage):
    return FileService(mock_file_manager, mock_storage)


# --- SAVE_WITH_NAME --- #


def test_save_with_name_success(service, mock_file_manager, mock_storage):
    service.save_with_name("backup")

    mock_storage.export_state.assert_called_once()
    args, _ = mock_file_manager.save.call_args
    # Перевіряємо структуру виклику з урахуванням timestamp
    assert args[0] == {"a": 1}
    assert args[1].startswith("backup_")
    assert args[1].endswith(".pkl")


def test_save_with_name_uses_default_name(service, mock_file_manager):
    service.save_with_name()  # без аргументу

    args, _ = mock_file_manager.save.call_args
    assert args[0] == {"a": 1}
    assert args[1].startswith("autosave_")
    assert args[1].endswith(".pkl")


def test_save_with_name_empty_data_raises(service, mock_storage):
    mock_storage.export_state.return_value = {}
    with pytest.raises(InvalidError, match="Data to save cannot be None or empty"):
        service.save_with_name("test")


def test_save_with_name_pickle_error(service, mock_storage):
    # lambda неможливо серіалізувати
    mock_storage.export_state.return_value = {"bad": lambda x: x}
    with pytest.raises(InvalidError, match="Cannot serialize data"):
        service.save_with_name("broken")


# --- LOAD_BY_NAME --- #


def test_load_by_name_success(service, mock_file_manager, mock_storage):
    mock_file_manager.has_file_with_name.return_value = True
    mock_file_manager.load.return_value = {"a": 1}

    service.load_by_name("backup.pkl")

    mock_file_manager.load.assert_called_once_with("backup.pkl")
    mock_storage.import_state.assert_called_once_with({"a": 1})


def test_load_by_name_missing_file(service, mock_file_manager):
    mock_file_manager.has_file_with_name.return_value = False
    with pytest.raises(InvalidError, match="does not exist"):
        service.load_by_name("missing.pkl")


# --- DELETE_BY_NAME --- #


def test_delete_by_name_success(service, mock_file_manager):
    mock_file_manager.has_file_with_name.return_value = True
    service.delete_by_name("old.pkl")
    mock_file_manager.delete.assert_called_once_with("old.pkl")


def test_delete_by_name_missing_file_raises(service, mock_file_manager):
    mock_file_manager.has_file_with_name.return_value = False
    with pytest.raises(InvalidError, match="does not exist"):
        service.delete_by_name("ghost.pkl")


# --- GET_FILE_LIST --- #


def test_get_file_list_returns_names(service, mock_file_manager):
    result = service.get_file_list()
    assert result == ["file1.pkl", "file2.pkl"]


def test_get_file_list_empty_raises(service, mock_file_manager):
    mock_file_manager.get_all_names.return_value = []
    with pytest.raises(InvalidError, match="No files available"):
        service.get_file_list()


# --- VALIDATION --- #


@pytest.mark.parametrize("bad_name", [None, 123, "   ", ""])
def test_validate_name_invalid(bad_name):
    with pytest.raises(InvalidError):
        FileService._validate_name(bad_name)


def test_validate_name_valid():
    FileService._validate_name("valid_name.pkl")









