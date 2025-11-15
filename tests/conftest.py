"""Global pytest configuration for all tests."""

import pytest

from bll.validation_policies.phone_validation_policy import PhoneValidationPolicy


@pytest.fixture(scope="session", autouse=True)
def setup_phone_validation():
    """Initialize phone validation policy for all tests."""
    PhoneValidationPolicy.set_region("UA")
    yield









