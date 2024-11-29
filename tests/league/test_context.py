"""Tests for league context."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import LeagueTier
from ea_nhl_stats.league.events import LeagueEvent, LeagueEventType
from ea_nhl_stats.league.context import LeagueContext, LeagueState
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.team import LeagueTeam
from ea_nhl_stats.league.models.trade import create_two_team_trade

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def league_context() -> LeagueContext:
    """Create league context for testing."""
    return LeagueContext(season=2024)


@pytest.fixture
def valid_team() -> LeagueTeam:
    """Create valid team for testing."""
    return LeagueTeam(
        name="Test Team",
        tier=LeagueTier.NHL
    )


@pytest.fixture
def valid_player() -> LeaguePlayer:
    """Create valid player for testing."""
    return LeaguePlayer(
        name="Test Player",
        position=Position.CENTER
    )


class TestLeagueState:
    """Test cases for LeagueState model."""
    
    def test_valid_state(self) -> None:
        """Test creation of valid state."""
        state = LeagueState(season=2024)
        assert state.season == 2024
        assert state.trade_deadline is None
        assert state.is_trading_allowed


class TestLeagueContext:
    """Test cases for LeagueContext."""
    
    def test_initial_state(self, league_context: LeagueContext) -> None:
        """Test initial league context state."""
        assert league_context.state.season == 2024
        assert not league_context.teams
        assert not league_context.players
        assert not league_context.pending_trades
    
    def test_register_team(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam
    ) -> None:
        """Test registering a team."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe to events
        league_context.event_bus.subscribe(
            LeagueEventType.TEAM_REGISTERED,
            handler
        )
        
        # Register team
        team = league_context.register_team(valid_team)
        assert team.team_id in league_context.teams
        assert league_context.teams[team.team_id] == team
        
        # Verify event
        assert len(received_events) == 1
        assert received_events[0].event_type == LeagueEventType.TEAM_REGISTERED
    
    def test_register_duplicate_team(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam
    ) -> None:
        """Test that registering duplicate team raises error."""
        league_context.register_team(valid_team)
        
        with pytest.raises(ValueError) as exc_info:
            league_context.register_team(valid_team)
        assert "already registered" in str(exc_info.value)
    
    def test_register_player(
        self,
        league_context: LeagueContext,
        valid_player: LeaguePlayer
    ) -> None:
        """Test registering a player."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe to events
        league_context.event_bus.subscribe(
            LeagueEventType.PLAYER_REGISTERED,
            handler
        )
        
        # Register player
        player = league_context.register_player(valid_player)
        assert player.player_id in league_context.players
        assert league_context.players[player.player_id] == player
        
        # Verify event
        assert len(received_events) == 1
        assert received_events[0].event_type == LeagueEventType.PLAYER_REGISTERED
    
    def test_register_duplicate_player(
        self,
        league_context: LeagueContext,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that registering duplicate player raises error."""
        league_context.register_player(valid_player)
        
        with pytest.raises(ValueError) as exc_info:
            league_context.register_player(valid_player)
        assert "already registered" in str(exc_info.value)
    
    def test_propose_trade(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test proposing a trade."""
        # Create second team and player
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        other_player = LeaguePlayer(
            name="Other Player",
            position=Position.CENTER
        )
        
        # Register teams and players
        team1 = league_context.register_team(valid_team)
        team2 = league_context.register_team(other_team)
        player1 = league_context.register_player(valid_player)
        player2 = league_context.register_player(other_player)
        
        # Sign players to teams
        player1 = player1.sign_with_team(
            team_id=team1.team_id,
            salary=1_000_000,
            length_years=2
        )
        player2 = player2.sign_with_team(
            team_id=team2.team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Create trade
        trade = create_two_team_trade(
            team1_id=team1.team_id,
            team1_players=[player1],
            team2_id=team2.team_id,
            team2_players=[player2]
        )
        
        # Track events
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        league_context.event_bus.subscribe(
            LeagueEventType.TRADE_PROPOSED,
            handler
        )
        
        # Propose trade
        league_context.propose_trade(trade)
        assert trade in league_context.pending_trades
        
        # Verify event
        assert len(received_events) == 1
        assert received_events[0].event_type == LeagueEventType.TRADE_PROPOSED
    
    def test_propose_trade_after_deadline(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that proposing trade after deadline raises error."""
        # Set trade deadline in past
        deadline = datetime.now() - timedelta(days=1)
        league_context.set_trade_deadline(deadline)
        
        # Create trade
        trade = create_two_team_trade(
            team1_id=valid_team.team_id,
            team1_players=[valid_player],
            team2_id=uuid4(),
            team2_players=[]
        )
        
        with pytest.raises(ValueError) as exc_info:
            league_context.propose_trade(trade)
        assert "deadline has passed" in str(exc_info.value)
    
    def test_execute_trade(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test executing a trade."""
        # Create second team and player
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        other_player = LeaguePlayer(
            name="Other Player",
            position=Position.CENTER
        )
        
        # Register teams and players
        team1 = league_context.register_team(valid_team)
        team2 = league_context.register_team(other_team)
        player1 = league_context.register_player(valid_player)
        player2 = league_context.register_player(other_player)
        
        # Sign players to teams
        player1 = player1.sign_with_team(
            team_id=team1.team_id,
            salary=1_000_000,
            length_years=2
        )
        player2 = player2.sign_with_team(
            team_id=team2.team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Create and propose trade
        trade = create_two_team_trade(
            team1_id=team1.team_id,
            team1_players=[player1],
            team2_id=team2.team_id,
            team2_players=[player2]
        )
        league_context.propose_trade(trade)
        
        # Track events
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        league_context.event_bus.subscribe(
            LeagueEventType.TRADE_EXECUTED,
            handler
        )
        
        # Execute trade
        updated_players = league_context.execute_trade(trade)
        assert trade not in league_context.pending_trades
        assert len(updated_players) == 2
        
        # Verify players were updated in registry
        for player in updated_players:
            assert league_context.players[player.player_id] == player
        
        # Verify event
        assert len(received_events) == 1
        assert received_events[0].event_type == LeagueEventType.TRADE_EXECUTED
    
    def test_execute_nonexistent_trade(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that executing nonexistent trade raises error."""
        trade = create_two_team_trade(
            team1_id=valid_team.team_id,
            team1_players=[valid_player],
            team2_id=uuid4(),
            team2_players=[]
        )
        
        with pytest.raises(ValueError) as exc_info:
            league_context.execute_trade(trade)
        assert "not found in pending trades" in str(exc_info.value)
    
    def test_reject_trade(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test rejecting a trade."""
        # Create second team and player
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        other_player = LeaguePlayer(
            name="Other Player",
            position=Position.CENTER
        )
        
        # Register teams and players
        team1 = league_context.register_team(valid_team)
        team2 = league_context.register_team(other_team)
        player1 = league_context.register_player(valid_player)
        player2 = league_context.register_player(other_player)
        
        # Sign players to teams
        player1 = player1.sign_with_team(
            team_id=team1.team_id,
            salary=1_000_000,
            length_years=2
        )
        player2 = player2.sign_with_team(
            team_id=team2.team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Create and propose trade
        trade = create_two_team_trade(
            team1_id=team1.team_id,
            team1_players=[player1],
            team2_id=team2.team_id,
            team2_players=[player2]
        )
        league_context.propose_trade(trade)
        
        # Track events
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        league_context.event_bus.subscribe(
            LeagueEventType.TRADE_REJECTED,
            handler
        )
        
        # Reject trade
        league_context.reject_trade(trade)
        assert trade not in league_context.pending_trades
        
        # Verify event
        assert len(received_events) == 1
        assert received_events[0].event_type == LeagueEventType.TRADE_REJECTED
    
    def test_reject_nonexistent_trade(
        self,
        league_context: LeagueContext,
        valid_team: LeagueTeam,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that rejecting nonexistent trade raises error."""
        trade = create_two_team_trade(
            team1_id=valid_team.team_id,
            team1_players=[valid_player],
            team2_id=uuid4(),
            team2_players=[]
        )
        
        with pytest.raises(ValueError) as exc_info:
            league_context.reject_trade(trade)
        assert "not found in pending trades" in str(exc_info.value)
    
    def test_season_lifecycle(self, league_context: LeagueContext) -> None:
        """Test season start/end cycle."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe to events
        league_context.event_bus.subscribe(
            LeagueEventType.SEASON_STARTED,
            handler
        )
        league_context.event_bus.subscribe(
            LeagueEventType.SEASON_ENDED,
            handler
        )
        
        # Start season
        league_context.start_season()
        assert league_context.state.is_trading_allowed
        assert league_context.state.trade_deadline is None
        
        # End season
        league_context.end_season()
        assert not league_context.state.is_trading_allowed
        assert league_context.state.season == 2025
        assert not league_context.pending_trades
        
        # Verify events
        assert len(received_events) == 2
        assert received_events[0].event_type == LeagueEventType.SEASON_STARTED
        assert received_events[1].event_type == LeagueEventType.SEASON_ENDED 