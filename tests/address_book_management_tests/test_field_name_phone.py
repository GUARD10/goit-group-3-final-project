import pytest

from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy
from dal.entities.field import Field
from dal.entities.name import Name
from dal.entities.phone import Phone


def test_field_equality():
    assert Field("abc") == Field("abc")
    assert Field("123") == "123"
    assert Field("abc") != Field("xyz")


def test_name_validation():
    with pytest.raises(TypeError):
        Name(None)

    with pytest.raises(TypeError):
        Name(123)

    with pytest.raises(ValueError):
        Name("")

    with pytest.raises(ValueError):
        Name("   ")

    name = Name("Roman")
    assert str(name) == "Roman"


def test_phone_validation_basic():
    # must be string
    with pytest.raises(TypeError):
        Phone(123)

    # empty or whitespace → invalid
    with pytest.raises(ValueError):
        Phone("")

    with pytest.raises(ValueError):
        Phone("   ")

    # otherwise accepted (no full validation here)
    assert Phone("12345").value == "12345"
    assert Phone("abc").value == "abc"
    assert Phone("+380991112233").value == "+380991112233"


def test_phone_policy_region_ua():
    PhoneValidationPolicy.set_region("UA")

    assert PhoneValidationPolicy.validate("+380991112233")
    assert PhoneValidationPolicy.validate("0991112233")

    assert not PhoneValidationPolicy.validate("abc")
    assert not PhoneValidationPolicy.validate("12345")
    assert not PhoneValidationPolicy.validate("+15551234567")


def test_phone_policy_region_us():
    PhoneValidationPolicy.set_region("US")

    assert PhoneValidationPolicy.validate("+1 555 123 4567")
    assert PhoneValidationPolicy.validate("(555) 123-4567")

    assert not PhoneValidationPolicy.validate("+380991112233")
    assert not PhoneValidationPolicy.validate("12")


def test_phone_policy_error_message():
    PhoneValidationPolicy.set_region("UA")

    msg = PhoneValidationPolicy.error_message("123")
    assert "Invalid UA phone number" in msg
    assert "Use +380" in msg
