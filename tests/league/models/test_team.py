"""Tests for team and team history models."""

import json
from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.models.team import LeagueTeam
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


def test_create_team():
    """Test creating a new team."""
    team = LeagueTeam(
        name="LG Blues",
        current_season=1,
        ea_club_id="1789"
    )
    
    assert team.name == "LG Blues"
    assert team.current_season == 1
    assert team.ea_club_id == "1789"
    assert len(team.player_ids) == 0
    assert len(team.manager_ids) == 0
    assert len(team.season_stats) == 0


def test_add_match(test_match):
    """Test adding a match to team history."""
    team = LeagueTeam(
        name="LG Blues",
        current_season=1,
        ea_club_id="1789"
    )
    
    # Add match
    team.add_match(test_match)
    
    # Verify season stats were created
    assert 1 in team.season_stats
    season = team.season_stats[1]
    
    # Verify match was added
    assert test_match.match_id in season.matches
    assert season.matches_played == 1
    
    # Verify stats were updated
    assert season.goals_for == 10
    assert season.goals_against == 11
    assert season.shots == 22
    assert season.powerplay_goals == 3
    assert season.powerplay_opportunities == 4
    assert season.time_on_attack == 421


def test_season_team_stats(test_match):
    """Test season team stats calculations."""
    team = LeagueTeam(
        name="LG Blues",
        current_season=1,
        ea_club_id="1789"
    )
    
    # Add match
    team.add_match(test_match)
    season = team.season_stats[1]
    
    # Test computed stats
    assert season.points == 0  # Lost the game
    assert season.win_percentage == 0.0
    assert season.goals_per_game == 10.0
    assert season.goals_against_per_game == 11.0
    assert season.goal_differential == -1
    assert season.shooting_percentage == round((10 / 22) * 100, 2)
    assert season.powerplay_percentage == round((3 / 4) * 100, 2)
    assert season.time_on_attack_per_game == 421.0


def test_roster_management():
    """Test team roster management."""
    team = LeagueTeam(
        name="LG Blues",
        current_season=1,
        ea_club_id="1789"
    )
    
    # Add players
    player1_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    player2_id = UUID('123e4567-e89b-12d3-a456-426614174001')
    
    team.add_player(player1_id)
    team.add_player(player2_id)
    assert len(team.player_ids) == 2
    assert player1_id in team.player_ids
    assert player2_id in team.player_ids
    
    # Remove player
    team.remove_player(player1_id)
    assert len(team.player_ids) == 1
    assert player1_id not in team.player_ids
    assert player2_id in team.player_ids
    
    # Add managers
    manager1_id = UUID('123e4567-e89b-12d3-a456-426614174002')
    manager2_id = UUID('123e4567-e89b-12d3-a456-426614174003')
    
    team.add_manager(manager1_id)
    team.add_manager(manager2_id)
    assert len(team.manager_ids) == 2
    assert manager1_id in team.manager_ids
    assert manager2_id in team.manager_ids
    
    # Remove manager
    team.remove_manager(manager1_id)
    assert len(team.manager_ids) == 1
    assert manager1_id not in team.manager_ids
    assert manager2_id in team.manager_ids
    