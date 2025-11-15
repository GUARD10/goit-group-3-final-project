from datetime import datetime

from dal.entities.note import Note


def test_note_init_creates_valid_entities():
    note = Note("my_note", "My Title", "Some long enough content")

    assert note.name.value == "my_note"
    assert note.title.value == "My Title"
    assert note.content.value == "Some long enough content"
    assert isinstance(note.created_at, datetime)
    assert note.updated_at is None


def test_note_str_contains_all_fields():
    note = Note("n", "Title", "Content with more than 10 chars")
    output = str(note)

    assert "📓 Title" in output
    assert "Name: n" in output
    assert "Created at:" in output
    assert "Updated at: Never" in output
    assert "Content with more than 10 chars" in output


def test_note_equality():
    n1 = Note("n", "T", "1234567890")
    n2 = Note("n", "T", "1234567890")

    assert n1 == n2
    assert hash(n1) == hash(n2)


def test_note_not_equal_to_other_types():
    assert Note("n", "t", "1234567890") != 123


def test_note_update_returns_builder():
    note = Note("n", "t", "1234567890")
    builder = note.update()
    assert hasattr(builder, "set_title")
    assert hasattr(builder, "build")
