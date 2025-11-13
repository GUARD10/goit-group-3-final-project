import pytest
from dal.entities.Content import Content


def test_content_valid():
    c = Content("1234567890")
    assert c.value == "1234567890"


def test_content_too_short():
    with pytest.raises(ValueError):
        Content("short")


def test_content_wrong_type():
    with pytest.raises(TypeError):
        Content(123)
