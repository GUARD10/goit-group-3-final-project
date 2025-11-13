import pytest
from dal.entities.Note import Note
from dal.entity_builders.note_builder.NoteBuilder import NoteBuilder


def test_note_builder_setters():
    note = Note("a", "b", "1234567890")
    builder = note.update()

    updated = (
        builder.set_name("new")
        .set_title("New Title")
        .set_content("Some long new content")
        .build()
    )

    assert updated.name.value == "new"
    assert updated.title.value == "New Title"
    assert updated.content.value == "Some long new content"


def test_note_builder_updates_timestamp():
    note = Note("a", "b", "1234567890")
    builder = note.update()
    updated = builder.set_title("X").build()

    assert updated.updated_at is not None
    assert updated.updated_at == updated.created_at


def test_note_builder_missing_fields_raises():
    note = Note("a", "b", "1234567890")
    builder = NoteBuilder(note)

    note.title = None  # simulate broken state

    with pytest.raises(ValueError):
        builder.build()
