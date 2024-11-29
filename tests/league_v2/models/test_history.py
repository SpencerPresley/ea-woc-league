"""Tests for player history models."""

import json
from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league_v2.models.history import SeasonStats
from ea_nhl_stats.league_v2.enums.types import Position
from ea_nhl_stats.models.game.ea_match import Match

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def ea_response_data():
    """Load test EA API response data."""
    with open("live_tests/output/ea_response.json") as f:
        return json.load(f)


@pytest.fixture
def test_match(ea_response_data):
    """Create a test match from EA API data."""
    return Match.model_validate(ea_response_data[0])


@pytest.fixture
def test_player_stats(test_match):
    """Get test player stats from match."""
    # vViperrz - Left Wing
    return test_match.players["1789"]["1669236396"]


def test_create_season_stats():
    """Test creating new season stats."""
    stats = SeasonStats(season=1)
    
    assert stats.season == 1
    assert stats.games_played == 0
    assert len(stats.game_stats) == 0
    assert len(stats.positions) == 0
    
    # Verify computed stats start at zero
    assert stats.goals == 0
    assert stats.assists == 0
    assert stats.points == 0
    assert stats.shots == 0
    assert stats.hits == 0
    assert stats.takeaways == 0
    assert stats.giveaways == 0
    assert stats.penalty_minutes == 0
    assert stats.plus_minus == 0


def test_add_game_stats(test_match, test_player_stats):
    """Test adding game stats to season."""
    stats = SeasonStats(season=1)
    
    # Add game stats
    stats.game_stats[test_match.match_id] = test_player_stats
    stats.games_played += 1
    stats.positions.add(Position.LEFT_WING)
    
    # Verify core stats
    assert stats.goals == 3
    assert stats.assists == 1
    assert stats.points == 4
    assert stats.shots == 6
    assert stats.hits == 10
    assert stats.takeaways == 0  # Actual value from data
    assert stats.giveaways == 16  # Actual value from data
    assert stats.penalty_minutes == 4  # Actual value from data
    assert stats.plus_minus == -2  # Actual value from data
    
    # Verify computed stats
    assert stats.shooting_percentage == 50.0  # 3 goals on 6 shots
    assert stats.points_per_game == 4.0  # 4 points in 1 game
    assert stats.takeaway_giveaway_ratio == 0.0  # 0 takeaways, 16 giveaways


def test_season_stats_zero_division():
    """Test season stats handle zero division cases."""
    stats = SeasonStats(season=1)
    
    # With no games played
    assert stats.shooting_percentage == 0.0
    assert stats.points_per_game == 0.0
    assert stats.takeaway_giveaway_ratio == 0.0


def test_position_tracking():
    """Test tracking positions played."""
    stats = SeasonStats(season=1)
    
    # Add some positions
    stats.positions.add(Position.CENTER)
    stats.positions.add(Position.LEFT_WING)
    stats.positions.add(Position.CENTER)  # Duplicate
    
    assert len(stats.positions) == 2
    assert Position.CENTER in stats.positions
    assert Position.LEFT_WING in stats.positions 