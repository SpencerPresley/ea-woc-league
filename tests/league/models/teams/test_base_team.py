"""Tests for base team model."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.types import Position, ManagerRole
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def test_team():
    """Create a test team."""
    return LeagueTeam(
        official_name="Test Team",
        league_level=LeagueLevel.NHL
    )


@pytest.fixture
def test_player():
    """Create a test player."""
    return LeaguePlayer(
        name="Test Player",
        position=Position.CENTER,
        ea_id="12345",
        ea_name="EA Test Player"
    )


def test_team_initialization(test_team):
    """Test team initialization."""
    assert test_team.official_name == "Test Team"
    assert test_team.league_level == LeagueLevel.NHL
    assert len(test_team.current_roster) == 0
    assert len(test_team.historical_players) == 0
    assert len(test_team.management) == 0


def test_add_roster_player(test_team, test_player):
    """Test adding a player to the roster."""
    test_team.add_roster_player(test_player)
    
    # Check current roster
    assert test_player.id in test_team.current_roster
    assert test_team.current_roster[test_player.id] == test_player
    
    # Check historical players
    assert test_player.id in test_team.historical_players
    assert test_team.historical_players[test_player.id] == test_player


def test_remove_roster_player(test_team, test_player):
    """Test removing a player from the roster."""
    # Add then remove player
    test_team.add_roster_player(test_player)
    test_team.remove_roster_player(test_player.id)
    
    # Should be removed from current roster but remain in history
    assert test_player.id not in test_team.current_roster
    assert test_player.id in test_team.historical_players


def test_add_manager(test_team, test_player):
    """Test adding a manager."""
    test_team.add_manager(test_player, ManagerRole.GM)
    
    # Should be in roster, history, and management
    assert test_player.id in test_team.current_roster
    assert test_player.id in test_team.historical_players
    assert test_player.id in test_team.management
    assert test_team.management[test_player.id] == ManagerRole.GM


def test_remove_manager(test_team, test_player):
    """Test removing a manager."""
    # Add then remove manager
    test_team.add_manager(test_player, ManagerRole.GM)
    test_team.remove_manager(test_player.id)
    
    # Should be removed from management but stay in roster
    assert test_player.id not in test_team.management
    assert test_player.id in test_team.current_roster
    assert test_player.id in test_team.historical_players


def test_manager_roster_protection(test_team, test_player):
    """Test that managers can't be removed from roster."""
    # Make player a manager
    test_team.add_manager(test_player, ManagerRole.GM)
    
    # Try to remove from roster
    test_team.remove_roster_player(test_player.id)
    
    # Should still be in roster
    assert test_player.id in test_team.current_roster
