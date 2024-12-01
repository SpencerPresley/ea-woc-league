"""Tests for the TierData model."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pytest_mock.plugin import MockerFixture

from ea_nhl_stats.league.models.season import TierData
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer
from ea_nhl_stats.league.enums.types import Position
from ea_nhl_stats.league.enums.league_level import LeagueLevel

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def tier_data() -> TierData:
    """Create a test tier."""
    return TierData()


@pytest.fixture
def team() -> LeagueTeam:
    """Create a test team."""
    return LeagueTeam(
        official_name=TeamIdentifier.ST_LOUIS_BLUES.value,
        league_level=LeagueLevel.NHL
    )


@pytest.fixture
def player() -> LeaguePlayer:
    """Create a test player."""
    return LeaguePlayer(
        name="Test Player",
        position=Position.CENTER
    )


def test_tier_data_initialization() -> None:
    """Test that TierData initializes with empty dictionaries."""
    tier = TierData()
    
    assert isinstance(tier.teams, dict)
    assert isinstance(tier.players, dict)
    assert len(tier.teams) == 0
    assert len(tier.players) == 0


def test_add_and_get_team(tier_data: TierData, team: LeagueTeam) -> None:
    """Test adding and retrieving a team."""
    team_id = TeamIdentifier.ST_LOUIS_BLUES
    
    # Add team
    tier_data.teams[team_id] = team
    
    # Get team
    assert tier_data.teams[team_id] == team


def test_add_and_get_player(tier_data: TierData, player: LeaguePlayer) -> None:
    """Test adding and retrieving a player."""
    player_id = player.id
    
    # Add player
    tier_data.players[player_id] = player
    
    # Get player
    assert tier_data.players[player_id] == player


def test_get_nonexistent_team(tier_data: TierData) -> None:
    """Test getting a team that doesn't exist raises KeyError."""
    with pytest.raises(KeyError):
        _ = tier_data.teams[TeamIdentifier.ST_LOUIS_BLUES]


def test_get_nonexistent_player(tier_data: TierData) -> None:
    """Test getting a player that doesn't exist raises KeyError."""
    with pytest.raises(KeyError):
        _ = tier_data.players[uuid4()]


def test_multiple_teams(tier_data: TierData) -> None:
    """Test adding multiple teams."""
    blues = LeagueTeam(
        official_name=TeamIdentifier.ST_LOUIS_BLUES.value,
        league_level=LeagueLevel.NHL
    )
    flames = LeagueTeam(
        official_name=TeamIdentifier.CALGARY_FLAMES.value,
        league_level=LeagueLevel.NHL
    )
    
    tier_data.teams[TeamIdentifier.ST_LOUIS_BLUES] = blues
    tier_data.teams[TeamIdentifier.CALGARY_FLAMES] = flames
    
    assert tier_data.teams[TeamIdentifier.ST_LOUIS_BLUES] == blues
    assert tier_data.teams[TeamIdentifier.CALGARY_FLAMES] == flames
    assert len(tier_data.teams) == 2


def test_multiple_players(tier_data: TierData) -> None:
    """Test adding multiple players."""
    player1 = LeaguePlayer(name="Player 1", position=Position.CENTER)
    player2 = LeaguePlayer(name="Player 2", position=Position.GOALIE)
    
    tier_data.players[player1.id] = player1
    tier_data.players[player2.id] = player2
    
    assert tier_data.players[player1.id] == player1
    assert tier_data.players[player2.id] == player2
    assert len(tier_data.players) == 2 