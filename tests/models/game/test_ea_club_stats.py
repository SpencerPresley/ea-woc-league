"""Tests for EA NHL club statistics models."""

import json
from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.models.game.ea_club_stats import ClubStats, AggregateStats

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def ea_response_data():
    """Load test EA API response data."""
    with open("live_tests/output/ea_response.json") as f:
        return json.load(f)


def test_parse_club_stats(ea_response_data):
    """Test parsing club stats from EA API response."""
    club_data = ea_response_data[0]["clubs"]["1789"]  # LG Blues
    
    club = ClubStats.model_validate(club_data)
    
    # Test basic info
    assert club.club_division == 10
    assert club.cnhl_online_game_type == "5"  # Game type code
    
    # Test game results
    assert club.goals == 10
    assert club.goals_against == 11
    assert club.goals_for_raw == 10
    assert club.goals_against_raw == 11
    assert club.score == 10
    assert club.opponent_score == 11
    
    # Test team stats
    assert club.passes_attempted == 97  # Actual value from data
    assert club.passes_completed == 76  # Actual value from data
    assert club.powerplay_goals == 3  # Actual value from data
    assert club.powerplay_opportunities == 4  # Actual value from data
    assert club.shots == 22  # Actual value from data
    assert club.time_on_attack == 421  # Actual value from data
    
    # Test team details
    assert club.details.name == "LG Blues"
    assert club.details.club_id == 1789
    assert club.details.team_id == 273  # Actual value from data


def test_parse_aggregate_stats(ea_response_data):
    """Test parsing aggregate stats from EA API response."""
    agg_data = ea_response_data[0]["aggregate"]["1789"]  # LG Blues
    
    agg = AggregateStats.model_validate(agg_data)
    
    # Test basic info
    assert agg.club_level == 57  # Actual club level
    assert agg.position == 0
    assert agg.team_id == 3000
    
    # Test game results
    assert agg.score == 60
    assert agg.opponent_score == 66
    
    # Test skater stats
    assert agg.skgoals == 10
    assert agg.skassists == 8
    assert agg.skshots == 20
    assert agg.skhits == 31
    assert agg.skpasses == 75
    assert agg.skpassattempts == 95
    assert agg.skpasspct == 395.42
    
    # Test goalie stats
    assert agg.glshots == 26
    assert agg.glsaves == 15
    assert agg.glga == 11
    assert agg.glsavepct == 0.58 