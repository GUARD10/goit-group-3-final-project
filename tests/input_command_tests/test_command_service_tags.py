import pytest

from bll.services.command_service.CommandService import CommandService
from bll.services.note_service.NoteService import NoteService
from dal.storages.NoteStorage import NoteStorage


class FakeRecordService:
    def __init__(self):
        self.records = {}


class FakeFileService:
    def is_save_able(self):
        return False

    def get_file_list(self):
        return []


class FakeInputService:
    def read_value(self, *args, **kwargs):
        return None

    def read_multiline(self, *args, **kwargs):
        return None

    def choose_from_list(self, *args, **kwargs):
        return None

    def choose_multiple_from_list(self, *args, **kwargs):
        return []


@pytest.fixture
def command_service():
    note_service = NoteService(NoteStorage())
    record_service = FakeRecordService()
    file_service = FakeFileService()
    input_service = FakeInputService()
    return CommandService(record_service, file_service, note_service, input_service)


def test_search_notes_command(command_service):
    ns = command_service.note_service
    ns.add("n1", "Quarterly Report", "Content long enough", tags=["urgent"])
    ns.add("n2", "Meeting Notes", "Discuss quarterly targets", tags=["work"])

    res = command_service.search_notes(["quarterly"])  # single token
    assert "Quarterly Report" in res
    assert "Meeting Notes" in res

    res2 = command_service.search_notes(["urgent"])  # tag token
    assert "Quarterly Report" in res2
    assert "Meeting Notes" not in res2


def test_show_all_notes_sorted_and_filtered(command_service):
    ns = command_service.note_service
    ns.add("n1", "Alpha", "Content long enough", tags=["b"])
    ns.add("n2", "Beta", "Content long enough", tags=["a"])
    ns.add("n3", "Gamma", "Content long enough")

    all_notes = command_service.show_all_notes()
    # sorted by primary tag then title; notes without tags last
    order_index = [all_notes.index(name) for name in ["Alpha", "Beta", "Gamma"]]
    assert order_index[1] < order_index[0] < order_index[2]

    filtered_notes = command_service.note_service.get_all_sorted_by_tags("a")
    assert [n.name.value for n in filtered_notes] == ["n2"]
