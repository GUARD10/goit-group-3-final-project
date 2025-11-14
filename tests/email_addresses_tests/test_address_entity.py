import pytest

from dal.entities.Address import Address


def test_address_valid_simple():
    addr = Address("Main street 10, Kyiv")
    assert addr.value == "Main street 10, Kyiv"
    assert str(addr) == "Main street 10, Kyiv"


def test_address_strips_spaces():
    addr = Address("   вул. Шевченка, 10, Київ   ")
    # перевіряємо, що обрізало тільки краї
    assert addr.value == "вул. Шевченка, 10, Київ"


def test_address_allows_long_text():
    text = "Київ, вул. Хрещатик, буд. 1, під'їзд 2, кв. 15, поверх 3"
    addr = Address(text)
    assert addr.value == text


@pytest.mark.parametrize("raw_address", ["", "   "])
def test_address_empty_raises_value_error(raw_address):
    with pytest.raises(ValueError):
        Address(raw_address)


def test_address_none_raises_value_error():
    with pytest.raises(ValueError):
        Address(None)  # type: ignore[arg-type]


def test_address_int_raises_type_error():
    with pytest.raises(TypeError):
        Address(123)  # type: ignore[arg-type]


def test_address_only_digits_raises_value_error():
    with pytest.raises(ValueError):
        Address("123123")


def test_address_without_letters_raises_value_error():
    with pytest.raises(ValueError):
        Address("12345-6789 #1")


def test_address_with_invalid_character_raises_value_error():
    with pytest.raises(ValueError):
        Address("Kyiv\tKhreshchatyk 1")

