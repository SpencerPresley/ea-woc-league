"""Tests for team models."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import LeagueTier
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.team import LeagueTeam, TeamRoster

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def valid_player() -> LeaguePlayer:
    """Create a valid player for testing."""
    return LeaguePlayer(
        name="Test Player",
        position=Position.CENTER
    )


@pytest.fixture
def valid_team() -> LeagueTeam:
    """Create a valid team for testing."""
    return LeagueTeam(
        name="Test Team",
        tier=LeagueTier.NHL
    )


@pytest.fixture
def signed_player(valid_player: LeaguePlayer, valid_team: LeagueTeam) -> LeaguePlayer:
    """Create a player signed to the test team."""
    return valid_player.sign_with_team(
        team_id=valid_team.team_id,
        salary=1_000_000,
        length_years=2
    )


class TestTeamRoster:
    """Test cases for TeamRoster model."""
    
    def test_empty_roster(self) -> None:
        """Test creation of empty roster."""
        roster = TeamRoster()
        assert not roster.active_players
        assert not roster.inactive_players
        assert not roster.all_players
        assert roster.total_salary == 0
    
    def test_add_active_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test adding active player to roster."""
        roster = TeamRoster()
        roster.add_player(signed_player)
        
        assert signed_player in roster.active_players
        assert signed_player not in roster.inactive_players
        assert signed_player in roster.all_players
        assert roster.total_salary == 1_000_000
    
    def test_add_inactive_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test adding inactive player to roster."""
        roster = TeamRoster()
        roster.add_player(signed_player, active=False)
        
        assert signed_player not in roster.active_players
        assert signed_player in roster.inactive_players
        assert signed_player in roster.all_players
        assert roster.total_salary == 1_000_000
    
    def test_add_duplicate_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test that adding duplicate player raises error."""
        roster = TeamRoster()
        roster.add_player(signed_player)
        
        with pytest.raises(ValueError) as exc_info:
            roster.add_player(signed_player)
        assert "already on roster" in str(exc_info.value)
    
    def test_remove_active_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test removing active player from roster."""
        roster = TeamRoster()
        roster.add_player(signed_player)
        roster.remove_player(signed_player)
        
        assert signed_player not in roster.active_players
        assert signed_player not in roster.inactive_players
        assert signed_player not in roster.all_players
        assert roster.total_salary == 0
    
    def test_remove_inactive_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test removing inactive player from roster."""
        roster = TeamRoster()
        roster.add_player(signed_player, active=False)
        roster.remove_player(signed_player)
        
        assert signed_player not in roster.active_players
        assert signed_player not in roster.inactive_players
        assert signed_player not in roster.all_players
        assert roster.total_salary == 0
    
    def test_remove_nonexistent_player(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test that removing nonexistent player raises error."""
        roster = TeamRoster()
        
        with pytest.raises(ValueError) as exc_info:
            roster.remove_player(signed_player)
        assert "not on roster" in str(exc_info.value)
    
    def test_set_player_status(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test changing player's active status."""
        roster = TeamRoster()
        roster.add_player(signed_player)
        
        # Change to inactive
        roster.set_player_status(signed_player, active=False)
        assert signed_player not in roster.active_players
        assert signed_player in roster.inactive_players
        
        # Change back to active
        roster.set_player_status(signed_player, active=True)
        assert signed_player in roster.active_players
        assert signed_player not in roster.inactive_players
    
    def test_set_nonexistent_player_status(
        self,
        signed_player: LeaguePlayer
    ) -> None:
        """Test that changing nonexistent player's status raises error."""
        roster = TeamRoster()
        
        with pytest.raises(ValueError) as exc_info:
            roster.set_player_status(signed_player, active=False)
        assert "not on roster" in str(exc_info.value)


class TestLeagueTeam:
    """Test cases for LeagueTeam model."""
    
    def test_valid_team(self, valid_team: LeagueTeam) -> None:
        """Test creation of valid team."""
        assert valid_team.name == "Test Team"
        assert valid_team.tier == LeagueTier.NHL
        assert isinstance(valid_team.team_id, UUID)
        assert isinstance(valid_team.roster, TeamRoster)
    
    def test_sign_player(
        self,
        valid_team: LeagueTeam,
        signed_player: LeaguePlayer
    ) -> None:
        """Test signing player to team."""
        player = valid_team.sign_player(signed_player)
        assert player in valid_team.roster.active_players
    
    def test_sign_wrong_team_player(
        self,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that signing player to wrong team raises error."""
        # Sign to different team
        other_team_id = uuid4()
        player = valid_player.sign_with_team(
            team_id=other_team_id,
            salary=1_000_000,
            length_years=2
        )
        
        with pytest.raises(ValueError) as exc_info:
            valid_team.sign_player(player)
        assert "not signed to team" in str(exc_info.value)
    
    def test_release_player(
        self,
        valid_team: LeagueTeam,
        signed_player: LeaguePlayer
    ) -> None:
        """Test releasing player from team."""
        # First add to roster
        valid_team.sign_player(signed_player)
        
        # Then release
        player = valid_team.release_player(signed_player)
        assert player.team_id is None
        assert player not in valid_team.roster.all_players
    
    def test_release_nonexistent_player(
        self,
        valid_team: LeagueTeam,
        signed_player: LeaguePlayer
    ) -> None:
        """Test that releasing nonexistent player raises error."""
        with pytest.raises(ValueError) as exc_info:
            valid_team.release_player(signed_player)
        assert "not on roster" in str(exc_info.value)
    
    def test_propose_trade(
        self,
        valid_team: LeagueTeam,
        signed_player: LeaguePlayer
    ) -> None:
        """Test proposing trade with another team."""
        # Create other team and player
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        other_player = LeaguePlayer(
            name="Other Player",
            position=Position.CENTER
        ).sign_with_team(
            team_id=other_team.team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Add players to rosters
        valid_team.sign_player(signed_player)
        other_team.sign_player(other_player)
        
        # Propose trade
        participant = valid_team.propose_trade(
            other_team=other_team,
            outgoing_players=[signed_player],
            incoming_players=[other_player]
        )
        
        assert participant.team_id == valid_team.team_id
        assert signed_player in participant.outgoing_players
        assert other_player in participant.incoming_players
    
    def test_propose_trade_wrong_roster(
        self,
        valid_team: LeagueTeam,
        signed_player: LeaguePlayer
    ) -> None:
        """Test that proposing trade with wrong roster raises error."""
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        
        with pytest.raises(ValueError) as exc_info:
            valid_team.propose_trade(
                other_team=other_team,
                outgoing_players=[signed_player],  # Not on roster
                incoming_players=[]
            )
        assert "not on" in str(exc_info.value) 