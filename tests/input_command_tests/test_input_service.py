import pytest
from bll.services.input_service.InputService import InputService
from dal.exceptions.InvalidException import InvalidException


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
    with pytest.raises(InvalidException):
        svc.handle("")


def test_parse_input_static():
    cmd, args = InputService._parse_input("add John 12345")
    assert cmd == "add"
    assert args == ["John", "12345"]
