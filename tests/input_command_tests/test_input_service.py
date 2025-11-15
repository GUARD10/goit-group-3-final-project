import pytest

from bll.services.input_service.input_service import InputService
from dal.exceptions.invalid_error import InvalidError


def test_handle_no_args():
    svc = InputService()
    cmd, args = svc.handle("hello")
    assert cmd == "hello"
    assert args == []


def test_handle_with_args():
    svc = InputService()
    cmd, args = svc.handle("echo Hello World")
    assert cmd == "echo"
    assert args == ["Hello", "World"]


def test_handle_invalid_empty():
    svc = InputService()
    with pytest.raises(InvalidError):
        svc.handle("")


def test_parse_input_static():
    cmd, args = InputService._parse_input("add John 12345")
    assert cmd == "add"
    assert args == ["John", "12345"]
