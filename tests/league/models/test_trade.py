"""Tests for trade models."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.trade import (
    TradeParticipant,
    TradePackage,
    create_two_team_trade
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def team1_id() -> UUID:
    """Create first team ID for testing."""
    return uuid4()


@pytest.fixture
def team2_id() -> UUID:
    """Create second team ID for testing."""
    return uuid4()


@pytest.fixture
def team1_player(team1_id: UUID) -> LeaguePlayer:
    """Create a player on team 1."""
    player = LeaguePlayer(
        name="Team 1 Player",
        position=Position.CENTER
    )
    return player.sign_with_team(
        team_id=team1_id,
        salary=1_000_000,
        length_years=2
    )


@pytest.fixture
def team2_player(team2_id: UUID) -> LeaguePlayer:
    """Create a player on team 2."""
    player = LeaguePlayer(
        name="Team 2 Player",
        position=Position.CENTER
    )
    return player.sign_with_team(
        team_id=team2_id,
        salary=1_000_000,
        length_years=2
    )


class TestTradeParticipant:
    """Test cases for TradeParticipant model."""
    
    def test_valid_participant(
        self,
        team1_id: UUID,
        team1_player: LeaguePlayer
    ) -> None:
        """Test creation of valid trade participant."""
        participant = TradeParticipant(
            team_id=team1_id,
            outgoing_players=[team1_player]
        )
        participant.validate_players()  # Should not raise
    
    def test_invalid_player_team(
        self,
        team1_id: UUID,
        team2_player: LeaguePlayer
    ) -> None:
        """Test validation fails if player not on team."""
        participant = TradeParticipant(
            team_id=team1_id,
            outgoing_players=[team2_player]
        )
        with pytest.raises(ValueError) as exc_info:
            participant.validate_players()
        assert "does not belong to team" in str(exc_info.value)
    
    def test_unsigned_player(
        self,
        team1_id: UUID
    ) -> None:
        """Test validation fails if player not signed."""
        player = LeaguePlayer(
            name="Unsigned Player",
            position=Position.CENTER,
            team_id=team1_id
        )
        participant = TradeParticipant(
            team_id=team1_id,
            outgoing_players=[player]
        )
        with pytest.raises(ValueError) as exc_info:
            participant.validate_players()
        assert "not under contract" in str(exc_info.value)


class TestTradePackage:
    """Test cases for TradePackage model."""
    
    def test_valid_trade(
        self,
        team1_id: UUID,
        team2_id: UUID,
        team1_player: LeaguePlayer,
        team2_player: LeaguePlayer
    ) -> None:
        """Test creation and execution of valid trade."""
        trade = create_two_team_trade(
            team1_id=team1_id,
            team1_players=[team1_player],
            team2_id=team2_id,
            team2_players=[team2_player]
        )
        
        # Execute trade
        updated_players = trade.execute_trade()
        
        # Verify results
        assert len(updated_players) == 2
        
        # Find players by original ID
        player1 = next(
            p for p in updated_players
            if p.player_id == team1_player.player_id
        )
        player2 = next(
            p for p in updated_players
            if p.player_id == team2_player.player_id
        )
        
        # Verify team changes
        assert player1.team_id == team2_id
        assert player2.team_id == team1_id
        
        # Verify history
        assert len(player1.history.transactions) == 2  # Sign + Trade
        assert len(player2.history.transactions) == 2
    
    def test_duplicate_player(
        self,
        team1_id: UUID,
        team2_id: UUID,
        team1_player: LeaguePlayer
    ) -> None:
        """Test validation fails if player appears twice."""
        trade = create_two_team_trade(
            team1_id=team1_id,
            team1_players=[team1_player],
            team2_id=team2_id,
            team2_players=[team1_player]  # Same player
        )
        
        with pytest.raises(ValueError) as exc_info:
            trade.execute_trade()
        assert "Duplicate players" in str(exc_info.value)
    
    def test_minimum_teams(
        self,
        team1_id: UUID,
        team1_player: LeaguePlayer
    ) -> None:
        """Test validation requires at least two teams."""
        with pytest.raises(ValidationError):
            TradePackage(
                participants=[
                    TradeParticipant(
                        team_id=team1_id,
                        outgoing_players=[team1_player]
                    )
                ]
            )
    
    def test_three_team_trade(
        self,
        team1_id: UUID,
        team2_id: UUID,
        team1_player: LeaguePlayer,
        team2_player: LeaguePlayer
    ) -> None:
        """Test three-team trade execution."""
        team3_id = uuid4()
        team3_player = LeaguePlayer(
            name="Team 3 Player",
            position=Position.CENTER
        ).sign_with_team(
            team_id=team3_id,
            salary=1_000_000,
            length_years=2
        )
        
        trade = TradePackage(
            participants=[
                TradeParticipant(
                    team_id=team1_id,
                    outgoing_players=[team1_player],
                    incoming_players=[team2_player]
                ),
                TradeParticipant(
                    team_id=team2_id,
                    outgoing_players=[team2_player],
                    incoming_players=[team3_player]
                ),
                TradeParticipant(
                    team_id=team3_id,
                    outgoing_players=[team3_player],
                    incoming_players=[team1_player]
                )
            ]
        )
        
        # Execute trade
        updated_players = trade.execute_trade()
        
        # Verify results
        assert len(updated_players) == 3
        
        # Find players by original ID
        player1 = next(
            p for p in updated_players
            if p.player_id == team1_player.player_id
        )
        player2 = next(
            p for p in updated_players
            if p.player_id == team2_player.player_id
        )
        player3 = next(
            p for p in updated_players
            if p.player_id == team3_player.player_id
        )
        
        # Verify team changes
        assert player1.team_id == team3_id
        assert player2.team_id == team1_id
        assert player3.team_id == team2_id 