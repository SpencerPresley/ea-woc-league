"""Tests for EA NHL API response integration with our models."""

import json
from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.ea_club_stats import ClubStats, AggregateStats
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats

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
    
    # Verify club stats
    blues = match.clubs["1789"]
    flames = match.clubs["45048"]
    
    assert blues.goals == 10
    assert blues.goals_against == 11
    assert flames.goals == 11 
    assert flames.goals_against == 10
    
    # Verify players
    assert len(match.players["1789"]) == 6  # Blues players
    assert len(match.players["45048"]) == 6  # Flames players
    
    # Verify aggregate stats
    assert match.aggregate["1789"].skgoals == 10
    assert match.aggregate["45048"].skgoals == 11


def test_parse_club_stats(ea_response_data):
    """Test parsing club stats from EA API response."""
    club_data = ea_response_data[0]["clubs"]["1789"]
    
    club = ClubStats.model_validate(club_data)
    
    assert club.club_division == 10
    assert club.goals == 10
    assert club.goals_against == 11
    assert club.team_side == 0
    assert club.details.name == "LG Blues"
    assert club.details.club_id == 1789


def test_parse_player_stats(ea_response_data):
    """Test parsing player stats from EA API response."""
    # Get a skater and goalie from first match
    skater_data = ea_response_data[0]["players"]["1789"]["1669236396"]  # vViperrz
    goalie_data = ea_response_data[0]["players"]["1789"]["1719294631"]  # Pxtlick
    
    skater = PlayerStats.model_validate(skater_data)
    goalie = PlayerStats.model_validate(goalie_data)
    
    # Verify skater stats
    assert skater.position == "leftWing"
    assert skater.skgoals == 3
    assert skater.skassists == 1
    assert skater.skshots == 6
    assert skater.skhits == 10
    
    # Verify goalie stats  
    assert goalie.position == "goalie"
    assert goalie.glsaves == 15
    assert goalie.glshots == 26
    assert goalie.glga == 11
    assert goalie.glsavepct == 0.58


def test_parse_aggregate_stats(ea_response_data):
    """Test parsing aggregate stats from EA API response."""
    agg_data = ea_response_data[0]["aggregate"]["1789"]
    
    agg = AggregateStats.model_validate(agg_data)
    
    assert agg.skgoals == 10
    assert agg.skassists == 8
    assert agg.skshots == 20
    assert agg.skhits == 31 