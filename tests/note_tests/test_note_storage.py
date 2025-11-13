from dal.entities.Note import Note
from dal.storages.NoteStorage import NoteStorage


def test_note_storage_add_and_find():
    storage = NoteStorage()
    note = Note("n", "t", "1234567890")

    storage.add(note)
    assert storage.find("n") == note


def test_note_storage_update():
    storage = NoteStorage()
    note = Note("n", "t", "1234567890")
    storage.add(note)

    updated = Note("n", "New", "0987654321")
    storage.update_item("n", updated)

    assert storage.find("n") == updated


def test_note_storage_has_and_delete():
    storage = NoteStorage()
    note = Note("n", "t", "1234567890")
    storage.add(note)

    assert storage.has("n")
    storage.delete("n")
    assert not storage.has("n")


def test_note_storage_all_values():
    storage = NoteStorage()
    n1 = Note("a", "t1", "1234567890")
    n2 = Note("b", "t2", "abcdefghij")

    storage.add(n1)
    storage.add(n2)

    values = storage.all_values()
    assert len(values) == 2
    assert n1 in values and n2 in values


def test_note_storage_filter():
    storage = NoteStorage()
    n1 = Note("a", "Hello", "1234567890")
    n2 = Note("b", "World", "abcdefghij")

    storage.add(n1)
    storage.add(n2)

    result = storage.filter(lambda n: n.title.value == "World")
    assert result == [n2]
