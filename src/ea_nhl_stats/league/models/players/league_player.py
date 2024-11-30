"""Player and manager models for the league management system.

This module defines the core player and manager models for the EA NHL league system.
It provides classes for tracking player statistics, managing roles, and handling
the relationship between players and managers.
"""

from typing import Optional, Dict, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.league.enums.types import Position, ManagerRole
from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.league.models.stats.player_stats import PlayerStats


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
    
    # Team associations
    current_team_id: Optional[UUID] = Field(
        default=None,
        description="Current team ID"
    )
    team_history: Set[UUID] = Field(
        default_factory=set,
        description="Set of all teams played for"
    )
    
    # Management info (if player is also a manager)
    manager_info: Optional[ManagerInfo] = Field(
        default=None,
        description="Management role information if player is a manager"
    )
    
    # Statistics tracking
    stats: PlayerStats = Field(
        default_factory=PlayerStats,
        description="Global player statistics"
    )
    
    # EA NHL integration
    ea_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL player ID"
    )
    ea_name: Optional[str] = Field(
        default=None,
        description="EA NHL display name"
    )
    discord_id: Optional[str] = Field(
        default=None,
        description="Discord user ID"
    )
    
    def join_team(self, team_id: UUID) -> None:
        """Record player joining a team.
        
        Args:
            team_id: UUID of the team being joined
        """
        self.current_team_id = team_id
        self.team_history.add(team_id)
    
    def leave_team(self) -> None:
        """Record player leaving their current team."""
        self.current_team_id = None
    
    def add_game_stats(self, match: Match, club_id: str) -> None:
        """Add statistics from a single game.
        
        This method processes match statistics and updates the player's
        global stats. It automatically creates the stats container if this is
        the first game.
        
        Args:
            match: The completed match
            club_id: The club ID the player was on
            
        Note:
            This method automatically updates all totals.
            The team's roster stats should be updated separately.
        """
        # Get player stats from match
        if not self.ea_id or club_id not in match.players:
            return  # Not our match
            
        player_stats = match.players[club_id].get(self.ea_id)
        if not player_stats:
            return  # Player not in match
            
        # Add game stats and update totals
        self.stats.games_played += 1
        
        # Generate UUID from match ID
        hex_str = match.match_id[:32].ljust(32, '0')
        match_uuid = UUID(hex_str)
        
        self.stats.game_stats[match_uuid] = player_stats
        self.stats.positions.add(self.position)  # Use pre-set position
    