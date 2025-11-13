import pytest

from dal.entities.Email import Email


def test_email_valid_simple():
    e = Email("user@example.com")
    assert e.value == "user@example.com"
    assert str(e) == "user@example.com"


def test_email_strips_spaces():
    e = Email("  john.doe@example.com  ")
    assert e.value == "john.doe@example.com"


def test_email_normalizes_domain_to_lowercase():
    e = Email("USER@EXAMPLE.COM")
    # локальна частина зберігається як є, домен → lower()
    assert e.value == "USER@example.com"


def test_email_with_plus_and_subdomain():
    e = Email("user+tag@sub.Domain.COM")
    # домен в lowercase
    assert e.value == "user+tag@sub.domain.com"


@pytest.mark.parametrize(
    "raw_email",
    [
        "",  # порожній рядок
        "   ",  # тільки пробіли
        "plainaddress",  # без @
        "no-at-sign.com",  # без @
        "@no-local-part.com",  # немає локальної частини
        "user@",  # немає домену
        "user@nodotdomain",  # домен без крапки
        "user@exa mple.com",  # пробіл у домені
        "us er@example.com",  # пробіл у локальній частині
    ],
)
def test_email_invalid_format_raises_value_error(raw_email):
    with pytest.raises(ValueError):
        Email(raw_email)


def test_email_consecutive_dots_in_local_raises():
    with pytest.raises(ValueError):
        Email("user..name@example.com")


def test_email_consecutive_dots_in_domain_raises():
    with pytest.raises(ValueError):
        Email("user@example..com")


def test_email_too_long_over_254_chars_raises():
    local = "a"
    domain = "b" * 250 + ".com"  # 1 + 1 + 250 + 4 = 256 символів
    long_email = f"{local}@{domain}"
    assert len(long_email) > 254
    with pytest.raises(ValueError):
        Email(long_email)


def test_email_local_part_longer_than_64_raises():
    local = "a" * 65
    long_local_email = f"{local}@example.com"
    with pytest.raises(ValueError):
        Email(long_local_email)


def test_email_value_none_raises_value_error():
    with pytest.raises(ValueError):
        Email(None)  # type: ignore[arg-type]


def test_email_non_str_type_raises_type_error():
    with pytest.raises(TypeError):
        Email(123)  # type: ignore[arg-type]
