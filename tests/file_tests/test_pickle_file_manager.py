import os
import pytest
from dal.file_managers.pickle_file_manager.PickleFileManager import PickleFileManager


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def manager(temp_dir):
    return PickleFileManager(base_dir=str(temp_dir))


def test_save_and_load_simple_object(manager):
    data = {"name": "Roman", "age": 29}
    manager.save(data, "user.pkl")

    # Переконуємось, що файл створено
    files = manager.get_all_names()
    assert "user.pkl" in files

    # Перевіряємо, що дані зчитуються коректно
    loaded_data = manager.load("user.pkl")
    assert loaded_data == data


def test_save_generates_unique_names(manager):
    data = {"a": 1}
    manager.save(data, "dup.pkl")
    manager.save(data, "dup.pkl")

    all_files = sorted(manager.get_all_names())
    assert all(f.startswith("dup") for f in all_files)
    assert len(all_files) == 2  # dup.pkl та dup_1.pkl


def test_load_raises_if_file_not_found(manager):
    with pytest.raises(FileNotFoundError):
        manager.load("missing.pkl")


def test_delete_removes_file(manager):
    data = {"test": True}
    manager.save(data, "todel.pkl")

    assert manager.has_file_with_name("todel.pkl")

    manager.delete("todel.pkl")
    assert not manager.has_file_with_name("todel.pkl")


def test_get_all_names_only_returns_pkl(manager):
    txt_path = os.path.join(manager.base_dir, "note.txt")
    with open(txt_path, "w") as f:
        f.write("not a pickle")

    manager.save({"x": 1}, "obj.pkl")

    all_files = manager.get_all_names()
    assert "obj.pkl" in all_files
    assert "note.txt" not in all_files


def test_normalize_adds_extension(manager):
    normalized = manager._normalize_name("backup")
    assert normalized.endswith(".pkl")


def test_has_file_with_name(manager):
    data = [1, 2, 3]
    manager.save(data, "arr.pkl")
    assert manager.has_file_with_name("arr.pkl")
    assert not manager.has_file_with_name("missing.pkl")
