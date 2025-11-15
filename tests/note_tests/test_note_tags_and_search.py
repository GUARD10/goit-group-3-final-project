import pytest

from bll.services.note_service.note_service import NoteService
from dal.storages.note_storage import NoteStorage


@pytest.fixture
def note_service():
    return NoteService(NoteStorage())


def test_add_note_with_tags_dedup_and_colors(note_service):
    note = note_service.add(
        "n1",
        "Quarterly Report",
        "Content long enough",
        tags=[("urgent", None), ("Work", "#009688"), "Work"],
    )

    names = [t.value for t in note.tags]
    assert names == ["Work", "urgent"] or names == ["urgent", "Work"]

    color_map = {t.value: t.color for t in note.tags}
    assert color_map["Work"] == "#009688"
    assert color_map["urgent"] is not None


def test_add_and_remove_tags(note_service):
    note_service.add("n1", "T", "Content long enough")

    updated = note_service.add_tags("n1", ["urgent", ("dev", "#03A9F4")])
    assert updated.has_tag("urgent")
    assert updated.has_tag("dev")
    assert updated.updated_at is not None

    updated2 = note_service.remove_tag("n1", "dev")
    assert not updated2.has_tag("dev")


def test_get_by_tag(note_service):
    note_service.add("n1", "T1", "Content long enough", tags=["urgent"])
    note_service.add("n2", "T2", "Content long enough", tags=["work"])
    note_service.add("n3", "T3", "Content long enough")

    urgent_notes = note_service.get_by_tag("urgent")
    assert [n.name.value for n in urgent_notes] == ["n1"]


def test_get_all_sorted_by_tags(note_service):
    note_service.add("n1", "Alpha", "Content long enough", tags=["b"])
    note_service.add("n2", "Beta", "Content long enough", tags=["a"])
    note_service.add("n3", "Gamma", "Content long enough")

    ordered = note_service.get_all_sorted_by_tags()
    names = [n.name.value for n in ordered]
    assert names[:2] == ["n2", "n1"]
    assert names[-1] == "n3"

    only_a = note_service.get_all_sorted_by_tags("a")
    assert [n.name.value for n in only_a] == ["n2"]


def test_get_distinct_tags(note_service):
    note_service.add("n1", "T1", "Content long enough", tags=["urgent", "work"])
    note_service.add("n2", "T2", "Content long enough", tags=["work", "dev"])

    distinct = note_service.get_distinct_tags()
    values = [t.value for t in distinct]
    assert values == sorted(set(values))
    assert set(values) >= {"urgent", "work", "dev"}


def test_search_by_title_content_and_tag(note_service):
    note_service.add("n1", "Quarterly Report", "Content long enough", tags=["urgent"])
    note_service.add("n2", "Meeting Notes", "Discuss quarterly targets", tags=["work"])

    res1 = note_service.search("urgent")
    assert [n.name.value for n in res1] == ["n1"]

    res2 = note_service.search("quarterly")
    names2 = sorted(n.name.value for n in res2)
    assert names2 == ["n1", "n2"]









