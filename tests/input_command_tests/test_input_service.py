import pytest
from bll.services.input_service.InputService import InputService
from dal.exceptions.InvalidException import InvalidException


class DummyCommand:
    def __init__(self, fn):
        self.handler = fn


class DummyCommandService:
    def __init__(self):
        self.commands = {
            "hello": DummyCommand(lambda: "Hi!"),
            "echo": DummyCommand(lambda args: f"Echo: {' '.join(args)}"),
        }

    def get_command(self, name):
        return self.commands.get(name)


def test_handle_no_args():
    svc = InputService(DummyCommandService())
    result = svc.handle("hello")
    assert result == "Hi!"


def test_handle_with_args():
    svc = InputService(DummyCommandService())
    result = svc.handle("echo Hello World")
    assert "Echo: Hello World" in result


def test_handle_invalid_command():
    svc = InputService(DummyCommandService())
    with pytest.raises(InvalidException):
        svc.handle("unknown")


def test_parse_input_static():
    cmd, args = InputService._parse_input("add John 12345")
    assert cmd == "add"
    assert args == ["John", "12345"]
