"""Tests for EA NHL match model."""

import json
from typing import TYPE_CHECKING

import pytest

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


def test_parse_match(ea_response_data):
    """Test parsing a full match from EA API response."""
    # Get first match from response
    match_data = ea_response_data[0]
    
    # Parse into Match model
    match = Match.model_validate(match_data)
    
    # Verify basic match data
    assert match.match_id == "14774884060144"
    assert match.timestamp == 1732867936
    assert match.time_ago.number == 7
    assert match.time_ago.unit == "hours"
    
    # Verify clubs
    assert len(match.clubs) == 2
    assert "1789" in match.clubs  # LG Blues
    assert "45048" in match.clubs  # LG Calgary Flames
    
    # Verify players
    assert len(match.players["1789"]) == 6  # Blues players
    assert len(match.players["45048"]) == 6  # Flames players
    
    # Verify aggregate stats exist
    assert "1789" in match.aggregate
    assert "45048" in match.aggregate


def test_match_properties(ea_response_data):
    """Test Match model helper properties."""
    match = Match.model_validate(ea_response_data[0])
    
    # Test home/away club IDs
    assert match.home_club_id == "1789"  # team_side = 0
    assert match.away_club_id == "45048"  # team_side = 1
    
    # Test home/away clubs
    assert match.home_club.details.name == "LG Blues"
    assert match.away_club.details.name == "LG Calgary Flames"
    
    # Test home/away players
    assert len(match.home_players) == 6
    assert len(match.away_players) == 6
    
    # Test home/away aggregates
    assert match.home_aggregate is not None
    assert match.away_aggregate is not None


def test_match_helper_methods(ea_response_data):
    """Test Match model helper methods."""
    match = Match.model_validate(ea_response_data[0])
    
    # Test get_club_players
    blues_players = match.get_club_players("1789")
    assert len(blues_players) == 6
    assert any(p.position == "goalie" for p in blues_players.values())
    
    # Test get_player_stats
    goalie = match.get_player_stats("1789", "1719294631")  # Pxtlick
    assert goalie is not None
    assert goalie.position == "goalie"
    
    # Test get_club_aggregate
    blues_agg = match.get_club_aggregate("1789")
    assert blues_agg is not None
    assert blues_agg.skgoals == 10 