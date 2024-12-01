"""Team models for the league management system.

This module defines the core team models and registry for managing teams
across different league levels.
"""

from typing import ClassVar, Dict, Optional, Set, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.league.models.stats.team_stats import TeamStats
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.types import ManagerRole

class LeagueTeam(BaseModel):
    """Abstract base team model for any hockey league level."""
    
    id: UUID = Field(default_factory=uuid4)
    official_name: str = Field(description="Official team name")
    league_level: LeagueLevel
    ea_club_id: Optional[str] = None
    ea_club_name: Optional[str] = None
    
    # Team stats from EA API
    stats: TeamStats = Field(
        default_factory=TeamStats,
        description="Team statistics from EA API"
    )
    
    # All players who have ever been on the team
    historical_players: Dict[UUID, LeaguePlayer] = Field(
        default_factory=dict,
        description="All players who have played for this team"
    )
    
    # Current active roster
    current_roster: Dict[UUID, LeaguePlayer] = Field(
        default_factory=dict,
        description="Currently active players"
    )
    
    # Management structure (player_id -> role)
    management: Dict[UUID, ManagerRole] = Field(
        default_factory=dict,
        description="Maps manager IDs to their roles"
    )
    
    def add_roster_player(self, player: LeaguePlayer) -> None:
        """Add a player to the team's current roster.
        
        This adds the player to both the current roster and historical players
        if they haven't played for the team before.
        
        Args:
            player: LeaguePlayer to add
        """
        # Add to current roster and historical players
        self.current_roster[player.id] = player
        self.historical_players[player.id] = player
    
    def remove_roster_player(self, player_id: UUID) -> None:
        """Remove a player from the current roster.
        
        Note:
            This only removes them from the current roster.
            Their record in historical_players is preserved.
            
        Args:
            player_id: UUID of the player to remove
        """
        if player_id not in self.management:  # Don't remove managers from roster
            self.current_roster.pop(player_id, None)
    
    def add_manager(self, player: LeaguePlayer, role: ManagerRole) -> None:
        """Add a manager to the team's staff.
        
        Args:
            player: LeaguePlayer to make manager
            role: Management role to assign
        """
        # Add to current roster and historical players
        self.add_roster_player(player)
        # Assign management role
        self.management[player.id] = role
    
    def remove_manager(self, player_id: UUID) -> None:
        """Remove a manager from the team's staff.
        
        Note:
            This only removes their management role.
            They remain on the roster as a player.
        """
        self.management.pop(player_id, None)
