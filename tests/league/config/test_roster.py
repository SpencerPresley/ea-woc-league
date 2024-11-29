"""Tests for roster configuration."""

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ea_nhl_stats.league.config.roster import PositionLimit, RosterLimits
from ea_nhl_stats.models.game.enums import Position

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


class TestPositionLimit:
    """Test cases for PositionLimit configuration."""
    
    def test_valid_limits(self) -> None:
        """Test creation with valid limits."""
        limit = PositionLimit(min_count=2, max_count=4)
        assert limit.min_count == 2
        assert limit.max_count == 4
    
    def test_equal_limits(self) -> None:
        """Test creation with equal min and max."""
        limit = PositionLimit(min_count=2, max_count=2)
        assert limit.min_count == limit.max_count == 2
    
    def test_invalid_limits(self) -> None:
        """Test that invalid limits raise ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            PositionLimit(min_count=4, max_count=2)
        assert "cannot be greater than" in str(exc_info.value)
    
    def test_negative_counts(self) -> None:
        """Test that negative counts raise ValidationError."""
        with pytest.raises(ValidationError):
            PositionLimit(min_count=-1, max_count=2)
        
        with pytest.raises(ValidationError):
            PositionLimit(min_count=0, max_count=-1)


class TestRosterLimits:
    """Test cases for RosterLimits configuration."""
    
    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        limits = RosterLimits()
        assert limits.max_players == 17
        assert limits.max_forwards == 9
        assert limits.max_defense == 6
        assert limits.max_goalies == 2
    
    def test_valid_totals(self) -> None:
        """Test that valid position totals are accepted."""
        limits = RosterLimits(
            max_players=17,
            max_forwards=9,
            max_defense=6,
            max_goalies=2
        )
        assert limits.max_players == 17
    
    def test_invalid_totals(self) -> None:
        """Test that invalid position totals raise ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            RosterLimits(
                max_players=17,
                max_forwards=10,  # Too many forwards
                max_defense=6,
                max_goalies=2
            )
        assert "must equal maximum players" in str(exc_info.value)
    
    def test_position_limits_validation(self) -> None:
        """Test validation of specific position limits."""
        # Valid position limits
        limits = RosterLimits(
            max_players=17,
            max_forwards=9,
            max_defense=6,
            max_goalies=2,
            position_limits={
                Position.LEFT_WING: PositionLimit(min_count=2, max_count=3),
                Position.CENTER: PositionLimit(min_count=2, max_count=3),
                Position.RIGHT_WING: PositionLimit(min_count=2, max_count=3),
                Position.LEFT_DEFENSE: PositionLimit(min_count=2, max_count=3),
                Position.RIGHT_DEFENSE: PositionLimit(min_count=2, max_count=3),
                Position.GOALIE: PositionLimit(min_count=2, max_count=2)
            }
        )
        assert limits.position_limits[Position.LEFT_WING].max_count == 3
        
        # Invalid forward totals
        with pytest.raises(ValueError) as exc_info:
            RosterLimits(
                max_players=17,
                max_forwards=9,
                max_defense=6,
                max_goalies=2,
                position_limits={
                    Position.LEFT_WING: PositionLimit(min_count=2, max_count=4),
                    Position.CENTER: PositionLimit(min_count=2, max_count=4),
                    Position.RIGHT_WING: PositionLimit(min_count=2, max_count=4)
                }
            )
        assert "cannot exceed maximum forwards" in str(exc_info.value)
    
    def test_create_default(self) -> None:
        """Test creation of default NHL-style limits."""
        limits = RosterLimits.create_default()
        
        # Check basic limits
        assert limits.max_players == 17
        assert limits.max_forwards == 9
        assert limits.max_defense == 6
        assert limits.max_goalies == 2
        
        # Check position-specific limits
        assert limits.position_limits[Position.LEFT_WING].min_count == 2
        assert limits.position_limits[Position.LEFT_WING].max_count == 3
        assert limits.position_limits[Position.CENTER].min_count == 2
        assert limits.position_limits[Position.CENTER].max_count == 3
        assert limits.position_limits[Position.RIGHT_WING].min_count == 2
        assert limits.position_limits[Position.RIGHT_WING].max_count == 3
        assert limits.position_limits[Position.LEFT_DEFENSE].min_count == 2
        assert limits.position_limits[Position.LEFT_DEFENSE].max_count == 3
        assert limits.position_limits[Position.RIGHT_DEFENSE].min_count == 2
        assert limits.position_limits[Position.RIGHT_DEFENSE].max_count == 3
        assert limits.position_limits[Position.GOALIE].min_count == 2
        assert limits.position_limits[Position.GOALIE].max_count == 2 