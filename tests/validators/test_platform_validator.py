"""Tests for the platform validator module."""

from typing import TYPE_CHECKING
import pytest

from ea_nhl_stats.validators.platform_validator import PlatformValidator

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

@pytest.fixture
def validator() -> PlatformValidator:
    """Create a PlatformValidator instance for testing.
    
    Returns:
        PlatformValidator: A new instance of PlatformValidator.
    """
    return PlatformValidator()

@pytest.mark.parametrize("platform", [
    "ps5",
    "ps4",
    "xbox-series-xs",
    "xboxone",
    "common-gen5"
])
def test_validate_valid_platform(validator: PlatformValidator, platform: str) -> None:
    """Test validation of valid platform identifiers.
    
    Args:
        validator: The PlatformValidator instance to test.
        platform: The platform identifier to validate.
    """
    assert validator.validate(platform) is True

@pytest.mark.parametrize("platform", [
    "",
    "invalid",
    "ps3",
    "xbox360",
    "pc"
])
def test_validate_invalid_platform(validator: PlatformValidator, platform: str) -> None:
    """Test validation of invalid platform identifiers.
    
    Args:
        validator: The PlatformValidator instance to test.
        platform: The platform identifier to validate.
    """
    assert validator.validate(platform) is False 