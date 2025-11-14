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

    def save_with_name(self, name="autosave"):
        return name

    def load_by_name(self, name):
        return True

    def delete_by_name(self, name):
        return True


class FakeRegistry:
    """Емуляція FileServiceRegistry"""
    def __init__(self):
        self._services = {
            "contacts": FakeFileService(),
            "notes": FakeFileService(),
        }

    def get(self, key: str):
        return self._services[key]

    def get_all(self):
        return self._services


class FakeInputService:
    def read_value(self, *a, **k): return None
    def read_multiline(self, *a, **k): return None
    def choose_from_list(self, *a, **k): return None
    def choose_multiple_from_list(self, *a, **k): return []


@pytest.fixture
def command_service():
    note_service = NoteService(NoteStorage())
    record_service = FakeRecordService()
    registry = FakeRegistry()
    input_service = FakeInputService()

    # ВАЖЛИВО! ПРАВИЛЬНИЙ ПОРЯДОК АРГУМЕНТІВ
    return CommandService(
        record_service=record_service,
        note_service=note_service,
        input_service=input_service,
        file_service_registry=registry,
    )


def test_search_notes_command(command_service):
    ns = command_service.note_service

    ns.add("n1", "Quarterly Report", "Content long enough", tags=["urgent"])
    ns.add("n2", "Meeting Notes", "Discuss quarterly targets", tags=["work"])

    # search by word
    res = command_service.search_notes(["quarterly"])
    assert "Quarterly Report" in res
    assert "Meeting Notes" in res  # у контенті є "quarterly"

    # search by tag
    res2 = command_service.search_notes(["urgent"])
    assert "Quarterly Report" in res2
    assert "Meeting Notes" not in res2


def test_show_all_notes_sorted_and_filtered(command_service):
    ns = command_service.note_service

    ns.add("n1", "Alpha", "Content long enough", tags=["b"])
    ns.add("n2", "Beta", "Content long enough", tags=["a"])
    ns.add("n3", "Gamma", "Content long enough")

    # This returns a string from show_all_notes()
    all_notes_str = command_service.show_all_notes()

    # Розкладаємо імена
    order = [all_notes_str.index(name) for name in ["Alpha", "Beta", "Gamma"]]

    # ORDER RULE:
    # tags sorted alphabetically → a < b → Beta, Alpha, then no-tag Gamma
    assert order[1] < order[0] < order[2]

    # Filtering by specific tag
    filtered_notes = ns.get_all_sorted_by_tags("a")
    assert [n.name.value for n in filtered_notes] == ["n2"]
