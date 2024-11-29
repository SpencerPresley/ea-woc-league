"""Tests for the match type validator module."""

from typing import TYPE_CHECKING
import pytest

from ea_nhl_stats.validators.match_type_validator import MatchTypeValidator

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

@pytest.fixture
def validator() -> MatchTypeValidator:
    """Create a MatchTypeValidator instance for testing.
    
    Returns:
        MatchTypeValidator: A new instance of MatchTypeValidator.
    """
    return MatchTypeValidator()

@pytest.mark.parametrize("match_type", [
    "gameType5",
    "gameType10",
    "club_private"
])
def test_validate_valid_match_type(validator: MatchTypeValidator, match_type: str) -> None:
    """Test validation of valid match type identifiers.
    
    Args:
        validator: The MatchTypeValidator instance to test.
        match_type: The match type identifier to validate.
    """
    assert validator.validate(match_type) is True

@pytest.mark.parametrize("match_type", [
    "",
    "invalid",
    "gameType1",
    "private_club",
    "public"
])
def test_validate_invalid_match_type(validator: MatchTypeValidator, match_type: str) -> None:
    """Test validation of invalid match type identifiers.
    
    Args:
        validator: The MatchTypeValidator instance to test.
        match_type: The match type identifier to validate.
    """
    assert validator.validate(match_type) is False 