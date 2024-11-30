"""Tests for player statistics model."""

import json
from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.models.stats.player_stats import PlayerStats
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats as EAPlayerStats
from ea_nhl_stats.league.enums.types import Position

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def ea_response_data():
    """Load test EA API response data."""
    with open("live_tests/output/ea_response.json") as f:
        return json.load(f)


def test_track_skater_stats(ea_response_data):
    """Test tracking skater stats from EA data."""
    # Get vViperrz's stats from the response
    skater_data = ea_response_data[0]["players"]["1789"]["1669236396"]
    ea_stats = EAPlayerStats.model_validate(skater_data)
    
    # Create our stats tracker
    stats = PlayerStats()
    match_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    
    # Add game stats
    stats.game_stats[match_id] = ea_stats
    stats.games_played += 1
    stats.positions.add(Position.LEFT_WING)
    
    # Test core stats
    assert stats.goals == 3
    assert stats.assists == 1
    assert stats.points == 4
    assert stats.shots == 6
    assert stats.hits == 10
    assert stats.takeaways == 0
    assert stats.giveaways == 16
    assert stats.penalty_minutes == 4
    assert stats.plus_minus == -2
    
    # Test computed stats
    assert stats.shooting_percentage == 50.0  # 3 goals on 6 shots
    assert stats.points_per_game == 4.0  # 4 points in 1 game
    assert stats.takeaway_giveaway_ratio == 0.0  # 0 takeaways, 16 giveaways


def test_track_goalie_stats(ea_response_data):
    """Test tracking goalie stats from EA data."""
    # Get Pxtlick's stats from the response
    goalie_data = ea_response_data[0]["players"]["1789"]["1719294631"]
    ea_stats = EAPlayerStats.model_validate(goalie_data)
    
    # Create our stats tracker
    stats = PlayerStats()
    match_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    
    # Add game stats
    stats.game_stats[match_id] = ea_stats
    stats.games_played += 1
    stats.positions.add(Position.GOALIE)
    
    # Test core stats - use actual values from the data
    assert stats.goals == ea_stats.skgoals
    assert stats.assists == ea_stats.skassists
    assert stats.points == ea_stats.skgoals + ea_stats.skassists
    assert stats.shots == ea_stats.skshots
    assert stats.hits == ea_stats.skhits
    assert stats.takeaways == ea_stats.sktakeaways
    assert stats.giveaways == ea_stats.skgiveaways
    assert stats.penalty_minutes == ea_stats.skpim
    assert stats.plus_minus == ea_stats.skplusmin
    
    # Test computed stats - only if they have shots/giveaways
    if ea_stats.skshots > 0:
        assert stats.shooting_percentage == (ea_stats.skgoals / ea_stats.skshots) * 100
    else:
        assert stats.shooting_percentage == 0.0
        
    assert stats.points_per_game == (ea_stats.skgoals + ea_stats.skassists) / 1  # 1 game
    
    if ea_stats.skgiveaways > 0:
        assert stats.takeaway_giveaway_ratio == ea_stats.sktakeaways / ea_stats.skgiveaways
    else:
        assert stats.takeaway_giveaway_ratio == 0.0
    