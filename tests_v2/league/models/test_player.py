"""Tests for player and manager models.

This module contains test cases for the league's player and manager models.
It verifies the core functionality of player statistics tracking, management
roles, and the relationship between players and managers.

The test cases are organized by class:
    - TestSeasonStats: Tests for season statistics tracking
    - TestLeaguePlayer: Tests for base player functionality
    - TestLeagueManager: Tests for manager-specific features
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.player_stats import PlayerStats
from ea_nhl_stats.league_v2.enums.types import ManagerRole
from ea_nhl_stats.league_v2.models.player import (
    SeasonStats,
    LeaguePlayer,
    LeagueManager
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def game_id() -> UUID:
    """Generate a test game ID.
    
    Returns:
        UUID: A unique identifier for test games
    """
    return uuid4()


@pytest.fixture
def team_id() -> UUID:
    """Generate a test team ID.
    
    Returns:
        UUID: A unique identifier for test teams
    """
    return uuid4()


@pytest.fixture
def player_stats() -> PlayerStats:
    """Create test player statistics.
    
    Returns:
        PlayerStats: Sample game statistics for testing
    """
    return PlayerStats(
        player_id=1,
        position=Position.CENTER,
        goals=1,
        assists=2,
        shots=5
    )


class TestSeasonStats:
    """Test cases for SeasonStats model."""
    
    def test_create_season_stats(self):
        """Test creating season statistics container."""
        stats = SeasonStats(season=1)
        assert stats.season == 1
        assert stats.games_played == 0
        assert not stats.game_stats
    
    def test_invalid_season_number(self):
        """Test validation of season numbers."""
        # Season must be positive
        with pytest.raises(ValidationError):
            SeasonStats(season=0)
        with pytest.raises(ValidationError):
            SeasonStats(season=-1)
    
    def test_games_played_validation(self):
        """Test validation of games played counter."""
        # Games played cannot be negative
        with pytest.raises(ValidationError):
            SeasonStats(season=1, games_played=-1)


class TestLeaguePlayer:
    """Test cases for LeaguePlayer model."""
    
    def test_create_player(self):
        """Test creating a basic player."""
        player = LeaguePlayer(
            name="John Doe",
            position=Position.CENTER,
            current_season=1
        )
        assert player.name == "John Doe"
        assert player.position == Position.CENTER
        assert player.current_season == 1
        assert not player.season_stats
    
    def test_add_game_stats(self, game_id, player_stats):
        """Test adding game statistics."""
        player = LeaguePlayer(
            name="John Doe",
            position=Position.CENTER,
            current_season=1
        )
        
        # Add first game
        player.add_game_stats(game_id, player_stats)
        assert 1 in player.season_stats
        assert player.season_stats[1].games_played == 1
        
        # Add another game
        new_game_id = uuid4()
        player.add_game_stats(new_game_id, player_stats)
        assert player.season_stats[1].games_played == 2
    
    def test_invalid_season(self):
        """Test season number validation."""
        with pytest.raises(ValidationError):
            LeaguePlayer(
                name="John Doe",
                position=Position.CENTER,
                current_season=0  # Must be positive
            )


class TestLeagueManager(TestLeaguePlayer):
    """Test cases for LeagueManager model.
    
    Inherits from TestLeaguePlayer to ensure managers maintain all player
    functionality.
    """
    
    def test_create_manager(self):
        """Test creating a player-manager."""
        manager = LeagueManager(
            name="John Doe",
            position=Position.CENTER,
            current_season=1,
            role=ManagerRole.GM
        )
        assert manager.name == "John Doe"
        assert manager.role == ManagerRole.GM
        assert manager.is_active_manager
        
        # Should still have player capabilities
        assert manager.position == Position.CENTER
        assert manager.current_season == 1
    
    def test_manager_inheritance(self, game_id, player_stats):
        """Test that managers retain player functionality."""
        manager = LeagueManager(
            name="John Doe",
            position=Position.CENTER,
            current_season=1,
            role=ManagerRole.GM
        )
        
        # Should be able to use player methods
        manager.add_game_stats(game_id, player_stats)
        assert manager.season_stats[1].games_played == 1 