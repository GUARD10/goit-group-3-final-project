import pytest
from dal.entities.Title import Title


def test_title_valid():
    t = Title("Hello")
    assert t.value == "Hello"


def test_title_empty_raises():
    with pytest.raises(ValueError):
        Title("")

    with pytest.raises(ValueError):
        Title("   ")


def test_title_wrong_type_raises():
    with pytest.raises(TypeError):
        Title(123)
