"""Tests for team statistics model."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.models.stats.team_stats import TeamStats

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def team_stats():
    """Fixture providing a basic team stats instance."""
    return TeamStats()


def test_team_stats_initialization(team_stats):
    """Test team stats initialization with default values."""
    assert team_stats.matches_played == 0
    assert team_stats.matches == {}
    assert team_stats.wins == 0
    assert team_stats.losses == 0
    assert team_stats.goals_for == 0
    assert team_stats.goals_against == 0
    assert team_stats.shots == 0
    assert team_stats.shots_against == 0
    assert team_stats.powerplay_goals == 0
    assert team_stats.powerplay_opportunities == 0
    assert team_stats.penalty_kill_goals_against == 0
    assert team_stats.penalty_kill_opportunities == 0
    assert team_stats.time_on_attack == 0
    assert team_stats.points == 0


def test_team_stats_derived_stats(team_stats):
    """Test team stats derived statistics calculations."""
    # Set some base stats
    team_stats.matches_played = 10
    team_stats.wins = 6
    team_stats.losses = 4
    team_stats.goals_for = 30
    team_stats.goals_against = 20
    team_stats.shots = 200
    team_stats.powerplay_opportunities = 20
    team_stats.powerplay_goals = 5
    team_stats.penalty_kill_opportunities = 15
    team_stats.penalty_kill_goals_against = 3
    team_stats.time_on_attack = 3000  # seconds
    
    # Test derived stats
    assert team_stats.win_percentage == 60.0  # (6/10) * 100
    assert team_stats.goals_per_game == 3.0  # 30 goals in 10 games
    assert team_stats.goals_against_per_game == 2.0  # 20 goals against in 10 games
    assert team_stats.goal_differential == 10  # 30 - 20
    assert team_stats.shooting_percentage == 15.0  # (30/200) * 100
    assert team_stats.powerplay_percentage == 25.0  # (5/20) * 100
    assert team_stats.penalty_kill_percentage == 80.0  # (1 - 3/15) * 100
    assert team_stats.time_on_attack_per_game == 300.0  # 3000/10


def test_team_stats_match_tracking(team_stats):
    """Test adding match results to team stats."""
    match_id = UUID("12345678-1234-5678-1234-567812345678")
    team_stats.matches[match_id] = {
        "goals": 5,
        "shots": 30,
        "powerplay_goals": 2,
        "powerplay_opportunities": 4,
        "penalty_kill_goals_against": 1,
        "penalty_kill_opportunities": 3,
        "time_on_attack": 600,  # seconds
    }
    
    assert len(team_stats.matches) == 1
    assert match_id in team_stats.matches
    match_data = team_stats.matches[match_id]
    assert match_data["goals"] == 5
    assert match_data["shots"] == 30
    assert match_data["powerplay_goals"] == 2
    assert match_data["powerplay_opportunities"] == 4
    assert match_data["penalty_kill_goals_against"] == 1
    assert match_data["penalty_kill_opportunities"] == 3
    assert match_data["time_on_attack"] == 600