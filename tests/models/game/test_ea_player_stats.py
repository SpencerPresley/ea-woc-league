"""Tests for EA NHL player statistics model."""

import json
from typing import TYPE_CHECKING

import pytest

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


def test_parse_skater_stats(ea_response_data):
    """Test parsing skater stats from EA API response."""
    # vViperrz - Left Wing
    skater_data = ea_response_data[0]["players"]["1789"]["1669236396"]
    
    skater = PlayerStats.model_validate(skater_data)
    
    # Test basic info
    assert skater.position == "leftWing"
    assert skater.player_name == "vViperrz"
    assert skater.player_level == 1  # Actual player level
    assert skater.player_level_display == 132  # Display level
    
    # Test game results
    assert skater.score == 10
    assert skater.opponent_score == 11
    
    # Test core stats
    assert skater.skgoals == 3
    assert skater.skassists == 1
    assert skater.skshots == 6
    assert skater.skhits == 10
    assert skater.skpasses == 12
    assert skater.skpassattempts == 19
    assert skater.skpasspct == 63.16
    
    # Test computed stats
    assert skater.points == 4
    assert skater.shots_missed == 3
    assert skater.shooting_percentage == 50.0
    assert skater.passes_missed == 7
    assert skater.passing_percentage == 63.16


def test_parse_goalie_stats(ea_response_data):
    """Test parsing goalie stats from EA API response."""
    # Pxtlick - Goalie
    goalie_data = ea_response_data[0]["players"]["1789"]["1719294631"]
    
    goalie = PlayerStats.model_validate(goalie_data)
    
    # Test basic info
    assert goalie.position == "goalie"
    assert goalie.player_name == "Pxtlick"
    assert goalie.player_level == 21  # Actual player level
    assert goalie.player_level_display == 0  # Display level
    
    # Test game results
    assert goalie.score == 10
    assert goalie.opponent_score == 11
    
    # Test core goalie stats
    assert goalie.glshots == 26
    assert goalie.glsaves == 15
    assert goalie.glga == 11
    assert goalie.glsavepct == 0.58
    assert goalie.glgaa == 11.0
    
    # Test breakaway stats
    assert goalie.glbrkshots == 4
    assert goalie.glbrksaves == 3
    assert goalie.glbrksavepct == 0.75
    
    # Test penalty shot stats
    assert goalie.glpenshots == 1
    assert goalie.glpensaves == 0
    assert goalie.glpensavepct == 0.0


def test_parse_player_ratings(ea_response_data):
    """Test parsing player ratings from EA API response."""
    # Test both skater and goalie ratings
    skater_data = ea_response_data[0]["players"]["1789"]["1669236396"]  # vViperrz
    goalie_data = ea_response_data[0]["players"]["1789"]["1719294631"]  # Pxtlick
    
    skater = PlayerStats.model_validate(skater_data)
    goalie = PlayerStats.model_validate(goalie_data)
    
    # Test skater ratings
    assert skater.rating_offense == 100.0
    assert skater.rating_defense == 20.0
    assert skater.rating_teamplay == 65.0
    
    # Test goalie ratings
    assert goalie.rating_offense == 30.0
    assert goalie.rating_defense == 75.0
    assert goalie.rating_teamplay == 35.0 