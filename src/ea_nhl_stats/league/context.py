"""League context for managing global state.

This module provides the central context for managing league state and
coordinating operations between components.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field

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
from ea_nhl_stats.league.models.trade import TradePackage


class LeagueState(BaseModel):
    """Current state of the league.
    
    Attributes:
        season: Current season year
        trade_deadline: Trade deadline date
        is_trading_allowed: Whether trades are currently allowed
    """
    
    season: int = Field(description="Current season year")
    trade_deadline: Optional[datetime] = Field(
        default=None,
        description="Trade deadline date"
    )
    is_trading_allowed: bool = Field(
        default=True,
        description="Whether trades are currently allowed"
    )


class LeagueContext:
    """Central context for league operations.
    
    This class manages global league state and coordinates operations
    between components.
    """
    
    def __init__(self, season: int = datetime.now().year) -> None:
        """Initialize league context.
        
        Args:
            season: Starting season year
        """
        self.state = LeagueState(season=season)
        self.event_bus = EventBus()
        
        self._teams: Dict[UUID, LeagueTeam] = {}
        self._players: Dict[UUID, LeaguePlayer] = {}
        self._pending_trades: List[TradePackage] = []
    
    @property
    def teams(self) -> Dict[UUID, LeagueTeam]:
        """Get all registered teams.
        
        Returns:
            Dict[UUID, LeagueTeam]: Map of team ID to team
        """
        return self._teams.copy()
    
    @property
    def players(self) -> Dict[UUID, LeaguePlayer]:
        """Get all registered players.
        
        Returns:
            Dict[UUID, LeaguePlayer]: Map of player ID to player
        """
        return self._players.copy()
    
    @property
    def pending_trades(self) -> List[TradePackage]:
        """Get all pending trades.
        
        Returns:
            List[TradePackage]: List of pending trades
        """
        return self._pending_trades.copy()
    
    def register_team(self, team: LeagueTeam) -> LeagueTeam:
        """Register a new team.
        
        Args:
            team: Team to register
            
        Returns:
            LeagueTeam: Registered team
            
        Raises:
            ValueError: If team already registered
        """
        if team.team_id in self._teams:
            raise ValueError(f"Team {team.name} already registered")
            
        self._teams[team.team_id] = team
        
        # Publish event
        self.event_bus.publish(
            TeamEvent(
                event_type=LeagueEventType.TEAM_REGISTERED,
                team_id=team.team_id,
                team=team
            )
        )
        
        return team
    
    def register_player(self, player: LeaguePlayer) -> LeaguePlayer:
        """Register a new player.
        
        Args:
            player: Player to register
            
        Returns:
            LeaguePlayer: Registered player
            
        Raises:
            ValueError: If player already registered
        """
        if player.player_id in self._players:
            raise ValueError(f"Player {player.name} already registered")
            
        self._players[player.player_id] = player
        
        # Publish event
        self.event_bus.publish(
            PlayerEvent(
                event_type=LeagueEventType.PLAYER_REGISTERED,
                player_id=player.player_id,
                player=player
            )
        )
        
        return player
    
    def propose_trade(self, trade: TradePackage) -> None:
        """Propose a new trade.
        
        Args:
            trade: Trade to propose
            
        Raises:
            ValueError: If trading not allowed or validation fails
        """
        if not self.state.is_trading_allowed:
            raise ValueError("Trading is not currently allowed")
            
        if self.state.trade_deadline:
            if datetime.now() > self.state.trade_deadline:
                raise ValueError("Trade deadline has passed")
        
        # Validate trade
        trade.validate_trade()
        
        # Add to pending trades
        self._pending_trades.append(trade)
        
        # Publish event
        self.event_bus.publish(
            TradeEvent(
                event_type=LeagueEventType.TRADE_PROPOSED,
                trade=trade,
                team_ids={p.team_id for p in trade.participants}
            )
        )
    
    def execute_trade(self, trade: TradePackage) -> List[LeaguePlayer]:
        """Execute a proposed trade.
        
        Args:
            trade: Trade to execute
            
        Returns:
            List[LeaguePlayer]: Updated player instances
            
        Raises:
            ValueError: If trade not pending or validation fails
        """
        if trade not in self._pending_trades:
            raise ValueError("Trade not found in pending trades")
            
        # Execute trade
        updated_players = trade.execute_trade()
        
        # Update player registry
        for player in updated_players:
            self._players[player.player_id] = player
        
        # Remove from pending trades
        self._pending_trades.remove(trade)
        
        # Publish event
        self.event_bus.publish(
            TradeEvent(
                event_type=LeagueEventType.TRADE_EXECUTED,
                trade=trade,
                team_ids={p.team_id for p in trade.participants}
            )
        )
        
        return updated_players
    
    def reject_trade(self, trade: TradePackage) -> None:
        """Reject a proposed trade.
        
        Args:
            trade: Trade to reject
            
        Raises:
            ValueError: If trade not pending
        """
        if trade not in self._pending_trades:
            raise ValueError("Trade not found in pending trades")
            
        # Remove from pending trades
        self._pending_trades.remove(trade)
        
        # Publish event
        self.event_bus.publish(
            TradeEvent(
                event_type=LeagueEventType.TRADE_REJECTED,
                trade=trade,
                team_ids={p.team_id for p in trade.participants}
            )
        )
    
    def set_trade_deadline(self, deadline: datetime) -> None:
        """Set the trade deadline.
        
        Args:
            deadline: New trade deadline
        """
        self.state.trade_deadline = deadline
        
        # Publish event
        self.event_bus.publish(
            LeagueEvent(
                event_type=LeagueEventType.TRADE_DEADLINE_PASSED,
                details={"deadline": deadline.isoformat()}
            )
        )
    
    def start_season(self) -> None:
        """Start a new season."""
        self.state.is_trading_allowed = True
        self.state.trade_deadline = None
        
        # Publish event
        self.event_bus.publish(
            LeagueEvent(
                event_type=LeagueEventType.SEASON_STARTED,
                details={"season": self.state.season}
            )
        )
    
    def end_season(self) -> None:
        """End the current season."""
        self.state.season += 1
        self.state.is_trading_allowed = False
        self._pending_trades.clear()
        
        # Publish event
        self.event_bus.publish(
            LeagueEvent(
                event_type=LeagueEventType.SEASON_ENDED,
                details={"season": self.state.season - 1}
            )
        ) 