"""Event system for league operations.

This module provides the event system for tracking and responding to
league operations.
"""

from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field

from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.team import LeagueTeam
from ea_nhl_stats.league.models.trade import TradePackage


class LeagueEventType(Enum):
    """Types of league events."""
    
    # Team events
    TEAM_REGISTERED = auto()
    TEAM_UPDATED = auto()
    
    # Player events
    PLAYER_REGISTERED = auto()
    PLAYER_SIGNED = auto()
    PLAYER_RELEASED = auto()
    PLAYER_STATUS_CHANGED = auto()
    
    # Trade events
    TRADE_PROPOSED = auto()
    TRADE_ACCEPTED = auto()
    TRADE_REJECTED = auto()
    TRADE_EXECUTED = auto()
    
    # Roster events
    ROSTER_UPDATED = auto()
    ROSTER_VALIDATED = auto()
    
    # League events
    SEASON_STARTED = auto()
    SEASON_ENDED = auto()
    TRADE_DEADLINE_PASSED = auto()


class LeagueEvent(BaseModel):
    """Base model for league events.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of event
        details: Additional event details
    """
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the event occurred"
    )
    event_type: LeagueEventType = Field(description="Type of event")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event details"
    )


class TeamEvent(LeagueEvent):
    """Event related to team operations.
    
    Attributes:
        team_id: ID of team involved
        team: Team data at time of event
    """
    
    team_id: UUID = Field(description="ID of team involved")
    team: LeagueTeam = Field(description="Team data at time of event")


class PlayerEvent(LeagueEvent):
    """Event related to player operations.
    
    Attributes:
        player_id: ID of player involved
        player: Player data at time of event
        team_id: ID of team involved (if any)
    """
    
    player_id: UUID = Field(description="ID of player involved")
    player: LeaguePlayer = Field(description="Player data at time of event")
    team_id: Optional[UUID] = Field(
        default=None,
        description="ID of team involved"
    )


class TradeEvent(LeagueEvent):
    """Event related to trade operations.
    
    Attributes:
        trade: Trade package involved
        team_ids: IDs of teams involved
    """
    
    trade: TradePackage = Field(description="Trade package involved")
    team_ids: Set[UUID] = Field(description="IDs of teams involved")


EventHandler = Callable[[LeagueEvent], None]


class EventBus:
    """Event bus for league operations.
    
    This class manages event publishing and subscription, allowing
    components to react to league operations.
    """
    
    def __init__(self) -> None:
        """Initialize event bus."""
        self._handlers: Dict[LeagueEventType, List[EventHandler]] = {
            event_type: [] for event_type in LeagueEventType
        }
    
    def subscribe(
        self,
        event_type: LeagueEventType,
        handler: EventHandler
    ) -> None:
        """Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to call when event occurs
        """
        self._handlers[event_type].append(handler)
    
    def unsubscribe(
        self,
        event_type: LeagueEventType,
        handler: EventHandler
    ) -> None:
        """Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            handler: Handler to remove
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    def publish(self, event: LeagueEvent) -> None:
        """Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        for handler in self._handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in event handler: {e}")  # TODO: Add proper logging
    
    def clear(self) -> None:
        """Remove all event handlers."""
        for event_type in LeagueEventType:
            self._handlers[event_type].clear() 