"""Team model for the league management system.

This module defines the core team model for tracking club data and match history.
It provides classes for managing team information, player rosters, and match records.
"""

from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.ea_club_stats import ClubStats
from ea_nhl_stats.league_v2.models.team_history import SeasonTeamStats


class LeagueTeam(BaseModel):
    """Base team model for all league clubs.
    
    This class represents a team in the league system. It tracks team information,
    player rosters, and match history. The class provides functionality for
    managing team statistics and EA NHL integration.
    """
    
    # Core team identification
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the team"
    )
    name: str = Field(description="Team's display name")
    
    # Statistics tracking
    current_season: int = Field(
        gt=0,  # Must be positive
        description="Current season number"
    )
    season_stats: Dict[int, SeasonTeamStats] = Field(
        default_factory=dict,
        description="Stats for each season"
    )
    
    # EA NHL integration
    ea_club_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL club ID"
    )
    
    # Roster tracking
    player_ids: Set[UUID] = Field(
        default_factory=set,
        description="UUIDs of current players"
    )
    manager_ids: Set[UUID] = Field(
        default_factory=set,
        description="UUIDs of current managers"
    )
    
    def add_match(self, match: Match) -> None:
        """Add a match to the team's history.
        
        This method processes a match and updates the current season's statistics.
        If this is the first match of the season, it automatically creates the
        season stats container.
        
        Args:
            match: The completed match to add
            
        Note:
            This method automatically updates all relevant season statistics.
        """
        # Create season stats if this is first match
        if self.current_season not in self.season_stats:
            self.season_stats[self.current_season] = SeasonTeamStats(
                season=self.current_season
            )
        
        # Get our club's stats from the match
        club_stats = None
        if str(self.ea_club_id) in match.clubs:
            club_stats = match.clubs[str(self.ea_club_id)]
        
        if not club_stats:
            return  # Not our match
            
        # Add match to history and update stats
        season = self.season_stats[self.current_season]
        season.add_match(match.match_id, club_stats)
    
    def add_player(self, player_id: UUID) -> None:
        """Add a player to the team's roster.
        
        Args:
            player_id: UUID of the player to add
        """
        self.player_ids.add(player_id)
    
    def remove_player(self, player_id: UUID) -> None:
        """Remove a player from the team's roster.
        
        Args:
            player_id: UUID of the player to remove
        """
        self.player_ids.discard(player_id)
    
    def add_manager(self, manager_id: UUID) -> None:
        """Add a manager to the team's staff.
        
        Args:
            manager_id: UUID of the manager to add
        """
        self.manager_ids.add(manager_id)
    
    def remove_manager(self, manager_id: UUID) -> None:
        """Remove a manager from the team's staff.
        
        Args:
            manager_id: UUID of the manager to remove
        """
        self.manager_ids.discard(manager_id) 