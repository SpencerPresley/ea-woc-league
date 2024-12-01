"""Tests for league player model."""

from typing import TYPE_CHECKING
from uuid import UUID
import json

import pytest

from ea_nhl_stats.league.enums.types import ManagerRole, Position
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer, ManagerInfo
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats as EAPlayerStats

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
def player_data():
    """Fixture providing basic player data."""
    return {
        "name": "Test Player",
        "position": Position.CENTER,
        "ea_id": "12345",
        "ea_name": "EA Test Player"
    }


@pytest.fixture
def test_ea_stats(ea_response_data):
    """Create test EA NHL stats."""
    # Use vViperrz data from the JSON
    skater_data = ea_response_data[0]["players"]["1789"]["1669236396"]
    return EAPlayerStats.model_validate(skater_data)


def test_league_player_initialization(player_data):
    """Test basic player initialization."""
    player = LeaguePlayer(**player_data)
    assert player.name == player_data["name"]
    assert player.position == player_data["position"]
    assert player.ea_id == player_data["ea_id"]
    assert player.ea_name == player_data["ea_name"]
    assert player.manager_info is None  # Not a manager by default
    assert len(player.team_stats) == 0  # No team stats yet
    assert player.current_team is None  # Not on a team yet


def test_league_player_with_manager_role():
    """Test player initialization with manager role."""
    manager_info = ManagerInfo(role=ManagerRole.GM, is_active=True)
    player = LeaguePlayer(
        name="Test Manager",
        position=Position.CENTER,
        ea_id="12345",
        ea_name="EA Test Manager",
        manager_info=manager_info
    )
    assert player.manager_info is not None
    assert player.manager_info.role == ManagerRole.GM
    assert player.manager_info.is_active is True


def test_league_player_team_management():
    """Test player team management methods."""
    player = LeaguePlayer(
        name="Test Player",
        position=Position.CENTER
    )
    team_id = TeamIdentifier.ST_LOUIS_BLUES
    
    # Test joining team
    player.join_team(team_id)
    assert player.current_team == team_id
    assert team_id in player.team_stats
    
    # Test leaving team
    player.leave_team()
    assert player.current_team is None
    assert team_id in player.team_stats  # Stats remain


def test_league_player_add_game_stats(player_data, test_ea_stats):
    """Test adding game stats to a player."""
    player = LeaguePlayer(**player_data)
    team_id = TeamIdentifier.ST_LOUIS_BLUES
    match_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    
    # Add stats for a game
    player.add_game_stats(team_id, match_id, test_ea_stats)
    
    # Verify stats were recorded
    assert team_id in player.team_stats
    team_stats = player.team_stats[team_id]
    assert team_stats.games_played == 1
    assert match_id in team_stats.game_stats
    assert team_stats.game_stats[match_id] == test_ea_stats
    assert player.position in team_stats.positions


def test_league_player_multiple_games_stats(player_data, test_ea_stats):
    """Test adding multiple games worth of stats."""
    player = LeaguePlayer(**player_data)
    team_id = TeamIdentifier.ST_LOUIS_BLUES
    match1_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    match2_id = UUID('123e4567-e89b-12d3-a456-426614174001')
    
    # Add stats for two games
    player.add_game_stats(team_id, match1_id, test_ea_stats)
    player.add_game_stats(team_id, match2_id, test_ea_stats)
    
    # Verify stats were accumulated
    team_stats = player.team_stats[team_id]
    assert team_stats.games_played == 2
    assert match1_id in team_stats.game_stats
    assert match2_id in team_stats.game_stats
    assert team_stats.goals == 6  # 3 goals per game
    assert team_stats.assists == 2  # 1 assist per game


def test_league_player_equality():
    """Test player equality comparison."""
    player1 = LeaguePlayer(
        name="Test Player",
        position=Position.CENTER,
        ea_id="12345",
        ea_name="EA Test Player"
    )
    # Create player2 with same ID as player1
    player2 = LeaguePlayer(
        id=player1.id,  # Same ID
        name="Test Player",
        position=Position.CENTER,
        ea_id="12345",
        ea_name="EA Test Player"
    )
    player3 = LeaguePlayer(
        name="Different Player",
        position=Position.CENTER,
        ea_id="67890",
        ea_name="EA Different Player"
    )
    
    assert player1 == player2  # Same ID
    assert player1 != player3  # Different ID
    assert player1 != "not a player"  # Different type


def test_league_player_str_representation():
    """Test player string representation."""
    player = LeaguePlayer(
        name="Test Player",
        position=Position.CENTER,
        ea_id="12345",
        ea_name="EA Test Player"
    )
    str_repr = str(player)
    assert "Test Player" in str_repr
    assert str(Position.CENTER) in str_repr
    assert str(player.id) in str_repr  # Check for formatted UUID


def test_league_player_invalid_position():
    """Test player initialization with invalid position."""
    with pytest.raises(ValueError):
        LeaguePlayer(
            name="Test Player",
            position="invalid",  # type: ignore
            ea_id="12345",
            ea_name="EA Test Player"
        )
    