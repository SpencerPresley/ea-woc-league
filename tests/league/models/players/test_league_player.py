"""Tests for league player model."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.enums.types import ManagerRole, Position
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer, ManagerInfo

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def player_data():
    """Fixture providing basic player data."""
    return {
        "name": "Test Player",
        "position": Position.CENTER,
        "ea_id": "12345",
        "ea_name": "EA Test Player"
    }


def test_league_player_initialization(player_data):
    """Test basic player initialization."""
    player = LeaguePlayer(**player_data)
    assert player.name == player_data["name"]
    assert player.position == player_data["position"]
    assert player.ea_id == player_data["ea_id"]
    assert player.ea_name == player_data["ea_name"]
    assert player.manager_info is None  # Not a manager by default


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
    team_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Test joining team
    player.join_team(team_id)
    assert player.current_team_id == team_id
    assert team_id in player.team_history
    
    # Test leaving team
    player.leave_team()
    assert player.current_team_id is None
    assert team_id in player.team_history  # History remains


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
    