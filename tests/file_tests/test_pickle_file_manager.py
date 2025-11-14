import pytest

from dal.file_managers.pickle_file_manager.PickleFileManager import PickleFileManager


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def manager(temp_dir):
    return PickleFileManager(base_dir=temp_dir)


def test_save_and_load_simple_object(manager):
    data = {"name": "Roman", "age": 29}
    manager.save(data, "user.pkl")

    files = manager.get_all_names()
    assert "user.pkl" in files

    loaded_data = manager.load("user.pkl")
    assert loaded_data == data


def test_save_generates_unique_names(manager):
    data = {"a": 1}
    manager.save(data, "dup.pkl")
    manager.save(data, "dup.pkl")

    all_files = sorted(manager.get_all_names())

    assert all(f.startswith("dup") for f in all_files)
    assert len(all_files) == 2  # dup.pkl, dup_1.pkl


def test_load_raises_if_file_not_found(manager):
    with pytest.raises(FileNotFoundError):
        manager.load("missing.pkl")


def test_delete_removes_file(manager):
    data = {"test": True}
    manager.save(data, "todel.pkl")

    assert manager.has_file_with_name("todel.pkl")

    manager.delete("todel.pkl")
    assert not manager.has_file_with_name("todel.pkl")


def test_get_all_names_only_returns_pkl(manager, temp_dir):
    txt_path = temp_dir / "note.txt"
    txt_path.write_text("not a pickle")

    manager.save({"x": 1}, "obj.pkl")

    files = manager.get_all_names()

    assert "obj.pkl" in files
    assert "note.txt" not in files


def test_normalize_adds_extension(manager):
    normalized = manager._normalize_name("backup")

    normalized_str = str(normalized)

    assert normalized_str.endswith(".pkl")


def test_has_file_with_name(manager):
    data = [1, 2, 3]
    manager.save(data, "arr.pkl")

    assert manager.has_file_with_name("arr.pkl")
    assert not manager.has_file_with_name("missing.pkl")
