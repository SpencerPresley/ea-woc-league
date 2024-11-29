"""Tests for league event system."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import LeagueTier
from ea_nhl_stats.league.events import (
    EventBus,
    LeagueEvent,
    LeagueEventType,
    PlayerEvent,
    TeamEvent,
    TradeEvent
)
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.team import LeagueTeam
from ea_nhl_stats.league.models.trade import TradePackage, create_two_team_trade

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def event_bus() -> EventBus:
    """Create event bus for testing."""
    return EventBus()


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


class TestLeagueEvent:
    """Test cases for LeagueEvent model."""
    
    def test_valid_event(self) -> None:
        """Test creation of valid event."""
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        assert isinstance(event.timestamp, datetime)
        assert event.event_type == LeagueEventType.SEASON_STARTED
        assert event.details["season"] == 2024


class TestTeamEvent:
    """Test cases for TeamEvent model."""
    
    def test_valid_team_event(self, valid_team: LeagueTeam) -> None:
        """Test creation of valid team event."""
        event = TeamEvent(
            event_type=LeagueEventType.TEAM_REGISTERED,
            team_id=valid_team.team_id,
            team=valid_team
        )
        assert event.team_id == valid_team.team_id
        assert event.team == valid_team


class TestPlayerEvent:
    """Test cases for PlayerEvent model."""
    
    def test_valid_player_event(
        self,
        valid_player: LeaguePlayer,
        valid_team: LeagueTeam
    ) -> None:
        """Test creation of valid player event."""
        event = PlayerEvent(
            event_type=LeagueEventType.PLAYER_SIGNED,
            player_id=valid_player.player_id,
            player=valid_player,
            team_id=valid_team.team_id
        )
        assert event.player_id == valid_player.player_id
        assert event.player == valid_player
        assert event.team_id == valid_team.team_id


class TestTradeEvent:
    """Test cases for TradeEvent model."""
    
    def test_valid_trade_event(
        self,
        valid_player: LeaguePlayer,
        valid_team: LeagueTeam
    ) -> None:
        """Test creation of valid trade event."""
        # Create second team and player
        other_team = LeagueTeam(
            name="Other Team",
            tier=LeagueTier.NHL
        )
        other_player = LeaguePlayer(
            name="Other Player",
            position=Position.CENTER
        )
        
        # Create trade
        trade = create_two_team_trade(
            team1_id=valid_team.team_id,
            team1_players=[valid_player],
            team2_id=other_team.team_id,
            team2_players=[other_player]
        )
        
        event = TradeEvent(
            event_type=LeagueEventType.TRADE_PROPOSED,
            trade=trade,
            team_ids={valid_team.team_id, other_team.team_id}
        )
        assert event.trade == trade
        assert len(event.team_ids) == 2
        assert valid_team.team_id in event.team_ids
        assert other_team.team_id in event.team_ids


class TestEventBus:
    """Test cases for EventBus."""
    
    def test_subscribe_and_publish(self, event_bus: EventBus) -> None:
        """Test subscribing to and publishing events."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe and publish
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, handler)
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        event_bus.publish(event)
        
        assert len(received_events) == 1
        assert received_events[0] == event
    
    def test_unsubscribe(self, event_bus: EventBus) -> None:
        """Test unsubscribing from events."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe, unsubscribe, and publish
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, handler)
        event_bus.unsubscribe(LeagueEventType.SEASON_STARTED, handler)
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        event_bus.publish(event)
        
        assert not received_events
    
    def test_multiple_handlers(self, event_bus: EventBus) -> None:
        """Test multiple handlers for same event type."""
        received_events1: List[LeagueEvent] = []
        received_events2: List[LeagueEvent] = []
        
        def handler1(event: LeagueEvent) -> None:
            received_events1.append(event)
            
        def handler2(event: LeagueEvent) -> None:
            received_events2.append(event)
        
        # Subscribe both handlers and publish
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, handler1)
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, handler2)
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        event_bus.publish(event)
        
        assert len(received_events1) == 1
        assert len(received_events2) == 1
        assert received_events1[0] == event
        assert received_events2[0] == event
    
    def test_handler_error(self, event_bus: EventBus) -> None:
        """Test that handler errors don't stop event processing."""
        received_events: List[LeagueEvent] = []
        
        def bad_handler(event: LeagueEvent) -> None:
            raise ValueError("Oops")
            
        def good_handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe both handlers and publish
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, bad_handler)
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, good_handler)
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        event_bus.publish(event)  # Should not raise
        
        assert len(received_events) == 1
        assert received_events[0] == event
    
    def test_clear(self, event_bus: EventBus) -> None:
        """Test clearing all handlers."""
        received_events: List[LeagueEvent] = []
        
        def handler(event: LeagueEvent) -> None:
            received_events.append(event)
        
        # Subscribe, clear, and publish
        event_bus.subscribe(LeagueEventType.SEASON_STARTED, handler)
        event_bus.clear()
        event = LeagueEvent(
            event_type=LeagueEventType.SEASON_STARTED,
            details={"season": 2024}
        )
        event_bus.publish(event)
        
        assert not received_events 