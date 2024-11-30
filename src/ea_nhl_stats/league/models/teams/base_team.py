"""Team models for the league management system.

This module defines the core team models and registry for managing teams
across different league levels.
"""

from typing import ClassVar, Dict, Optional, Set, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.league.models.stats.team_stats import TeamStats
from ea_nhl_stats.league.models.stats.player_stats import PlayerStats
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
    
    # All players who have ever been on the team and their stats
    historical_players: Dict[UUID, PlayerStats] = Field(
        default_factory=dict,
        description="Stats for all players who have played for this team"
    )
    
    # Current active roster
    current_roster: Set[UUID] = Field(
        default_factory=set,
        description="Currently active players"
    )
    
    # Management structure (player_id -> role)
    management: Dict[UUID, ManagerRole] = Field(
        default_factory=dict,
        description="Maps manager IDs to their roles"
    )
    
    def add_roster_player(self, player_id: UUID) -> None:
        """Add a player to the team's current roster.
        
        This adds the player to both the current roster and historical players
        if they haven't played for the team before.
        
        Args:
            player_id: UUID of the player to add
        """
        # Add to current roster
        self.current_roster.add(player_id)
        
        # Initialize stats if first time on team
        if player_id not in self.historical_players:
            self.historical_players[player_id] = PlayerStats()
    
    def remove_roster_player(self, player_id: UUID) -> None:
        """Remove a player from the current roster.
        
        Note:
            This only removes them from the current roster.
            Their stats history with the team is preserved.
            
        Args:
            player_id: UUID of the player to remove
        """
        if player_id not in self.management:  # Don't remove managers from roster
            self.current_roster.discard(player_id)
    
    def add_manager(self, player_id: UUID, role: ManagerRole) -> None:
        """Add a manager to the team's staff.
        
        Args:
            player_id: UUID of the player to make manager
            role: Management role to assign
        """
        # Add to current roster and historical players
        self.add_roster_player(player_id)
        # Assign management role
        self.management[player_id] = role
    
    def remove_manager(self, player_id: UUID) -> None:
        """Remove a manager from the team's staff.
        
        Note:
            This only removes their management role.
            They remain on the roster as a player.
        """
        self.management.pop(player_id, None)
    
    def update_player_stats(self, player_id: UUID, match_id: UUID, stats: PlayerStats) -> None:
        """Update stats for a player on this team.
        
        Args:
            player_id: UUID of the player
            match_id: UUID of the match
            stats: The player's stats for the match
        """
        if player_id not in self.historical_players:
            self.historical_players[player_id] = PlayerStats()
            
        player_stats = self.historical_players[player_id]
        player_stats.games_played += 1
        player_stats.game_stats[match_id] = stats