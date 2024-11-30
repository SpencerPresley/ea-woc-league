"""Tests for the base team model.

This module contains tests for the LeagueTeam class, which is the core team model
for the league management system.
"""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest

from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.stats.player_stats import PlayerStats
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.types import ManagerRole

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def test_team() -> LeagueTeam:
    """Create a test team instance."""
    return LeagueTeam(
        official_name="Test Team",
        league_level=LeagueLevel.NHL,
        ea_club_id="12345",
        ea_club_name="EA Test Team"
    )


@pytest.fixture
def test_player_id() -> UUID:
    """Create a test player UUID."""
    return uuid4()


@pytest.fixture
def test_match_id() -> UUID:
    """Create a test match UUID."""
    return uuid4()


def test_create_team(test_team: LeagueTeam) -> None:
    """Test creating a new team."""
    assert test_team.official_name == "Test Team"
    assert test_team.league_level == LeagueLevel.NHL
    assert test_team.ea_club_id == "12345"
    assert test_team.ea_club_name == "EA Test Team"
    assert isinstance(test_team.id, UUID)
    
    # Verify collections are initialized empty
    assert len(test_team.current_roster) == 0
    assert len(test_team.historical_players) == 0
    assert len(test_team.management) == 0


def test_add_roster_player(test_team: LeagueTeam, test_player_id: UUID) -> None:
    """Test adding a player to the roster."""
    test_team.add_roster_player(test_player_id)
    
    # Verify player is in roster
    assert test_player_id in test_team.current_roster
    
    # Verify stats were initialized
    assert test_player_id in test_team.historical_players
    assert isinstance(test_team.historical_players[test_player_id], PlayerStats)


def test_remove_roster_player(test_team: LeagueTeam, test_player_id: UUID) -> None:
    """Test removing a player from the roster."""
    # Add then remove player
    test_team.add_roster_player(test_player_id)
    test_team.remove_roster_player(test_player_id)
    
    # Verify player is removed from roster
    assert test_player_id not in test_team.current_roster
    
    # Verify stats history is preserved
    assert test_player_id in test_team.historical_players


def test_add_manager(test_team: LeagueTeam, test_player_id: UUID) -> None:
    """Test adding a manager to the team."""
    test_team.add_manager(test_player_id, ManagerRole.GM)
    
    # Verify manager role is set
    assert test_team.management[test_player_id] == ManagerRole.GM
    
    # Verify manager is also on roster
    assert test_player_id in test_team.current_roster
    assert test_player_id in test_team.historical_players


def test_remove_manager(test_team: LeagueTeam, test_player_id: UUID) -> None:
    """Test removing a manager from the team."""
    # Add then remove manager
    test_team.add_manager(test_player_id, ManagerRole.GM)
    test_team.remove_manager(test_player_id)
    
    # Verify manager role is removed
    assert test_player_id not in test_team.management
    
    # Verify they remain on roster as player
    assert test_player_id in test_team.current_roster
    assert test_player_id in test_team.historical_players


def test_manager_roster_protection(test_team: LeagueTeam, test_player_id: UUID) -> None:
    """Test that managers cannot be removed from roster."""
    # Add as manager
    test_team.add_manager(test_player_id, ManagerRole.GM)
    
    # Try to remove from roster
    test_team.remove_roster_player(test_player_id)
    
    # Verify still on roster
    assert test_player_id in test_team.current_roster


def test_update_player_stats(
    test_team: LeagueTeam,
    test_player_id: UUID,
    test_match_id: UUID
) -> None:
    """Test updating player statistics."""
    # Create test stats
    test_stats = PlayerStats()
    
    # Update stats for player
    test_team.update_player_stats(test_player_id, test_match_id, test_stats)
    
    # Verify stats were recorded
    player_stats = test_team.historical_players[test_player_id]
    assert player_stats.games_played == 1
    assert test_match_id in player_stats.game_stats
    assert player_stats.game_stats[test_match_id] == test_stats


def test_update_existing_player_stats(
    test_team: LeagueTeam,
    test_player_id: UUID,
    test_match_id: UUID
) -> None:
    """Test updating stats for existing player."""
    # Add player first
    test_team.add_roster_player(test_player_id)
    initial_stats = test_team.historical_players[test_player_id]
    
    # Update their stats
    new_stats = PlayerStats()
    test_team.update_player_stats(test_player_id, test_match_id, new_stats)
    
    # Verify stats were updated
    assert test_team.historical_players[test_player_id] == initial_stats
    assert test_team.historical_players[test_player_id].games_played == 1
    assert test_match_id in test_team.historical_players[test_player_id].game_stats
    