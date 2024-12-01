"""Player and manager models for the league management system.

This module defines the core player and manager models for the EA NHL league system.
It provides classes for tracking player statistics, managing roles, and handling
the relationship between players and managers.
"""

from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.league.enums.types import Position, ManagerRole
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.stats.player_stats import PlayerStats
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats as EAPlayerStats


class ManagerInfo(BaseModel):
    """Information about a player's management role.
    
    This class represents management responsibilities that a player may have.
    It encapsulates all management-related data that was previously part of
    the LeagueManager class.
    
    Attributes:
        role: The management role within the team
        is_active: Whether currently active in management role
    """
    
    role: ManagerRole = Field(description="Management role within the team")
    is_active: bool = Field(
        default=True,
        description="Whether currently active in management role"
    )


class LeaguePlayer(BaseModel):
    """Base player model for all league participants.
    
    This class represents a player in the league system. Players can optionally
    have management responsibilities through the manager_info field. The class
    provides functionality for tracking player statistics, team associations,
    and EA NHL integration.
    """
    
    # Core player identification
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the player"
    )
    name: str = Field(description="Player's display name")
    position: Position = Field(description="Player's primary position")
    
    # EA NHL integration
    ea_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL player ID"
    )
    ea_name: Optional[str] = Field(
        default=None,
        description="EA NHL display name"
    )
    
    # Management info (if player is also a manager)
    manager_info: Optional[ManagerInfo] = Field(
        default=None,
        description="Management role information if player is a manager"
    )
    
    # Team-specific stats
    team_stats: Dict[TeamIdentifier, PlayerStats] = Field(
        default_factory=dict,
        description="Stats for each team played for, keyed by team identifier"
    )
    
    # Current team
    current_team: Optional[TeamIdentifier] = Field(
        default=None,
        description="Current team identifier"
    )
    
    def join_team(self, team_id: TeamIdentifier) -> None:
        """Record player joining a team.
        
        Args:
            team_id: TeamIdentifier of the team being joined
        """
        self.current_team = team_id
        if team_id not in self.team_stats:
            self.team_stats[team_id] = PlayerStats()
    
    def leave_team(self) -> None:
        """Record player leaving their current team."""
        self.current_team = None
    
    def add_game_stats(self, team_id: TeamIdentifier, match_id: UUID, stats: EAPlayerStats) -> None:
        """Add game statistics for a specific team.
        
        Args:
            team_id: The team identifier the stats are for
            match_id: The match identifier
            stats: The EA NHL stats from the match
            
        Note:
            If this is the first game with this team, it will create the stats container.
            Stats are added to the team's stats even if it's not the player's current team.
        """
        # Initialize team stats if needed
        if team_id not in self.team_stats:
            self.team_stats[team_id] = PlayerStats()
            
        # Add game stats
        team_stats = self.team_stats[team_id]
        team_stats.games_played += 1
        team_stats.game_stats[match_id] = stats
        team_stats.positions.add(self.position)  # Track position played

