"""
Models for EA NHL match data.

This module provides models for match-level data from the EA NHL API,
including the relationships between clubs and players.
"""

from typing import Dict
from pydantic import BaseModel, Field

from ea_nhl_stats.models.game.ea_club_stats import ClubStats, AggregateStats
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats


class TimeAgo(BaseModel):
    """Time elapsed since the match."""
    
    number: int
    unit: str


class Match(BaseModel):
    """
    Complete match data including all clubs and players.
    
    This model represents a single game, containing:
    - Match identification and timing
    - Club data for both teams
    - Player statistics for all players
    - Aggregate team statistics
    """
    
    # Match Identification
    match_id: str = Field(alias="matchId")
    timestamp: int
    time_ago: TimeAgo = Field(alias="timeAgo")
    
    # Team Data
    clubs: Dict[str, ClubStats]  # club_id -> club stats
    players: Dict[str, Dict[str, PlayerStats]]  # club_id -> {player_id -> player stats}
    aggregate: Dict[str, AggregateStats]  # club_id -> aggregate stats
    
    @property
    def home_club_id(self) -> str:
        """Get the ID of the home club (team_side = 0)."""
        for club_id, club in self.clubs.items():
            if club.team_side == 0:
                return club_id
        return None
    
    @property
    def away_club_id(self) -> str:
        """Get the ID of the away club (team_side = 1)."""
        for club_id, club in self.clubs.items():
            if club.team_side == 1:
                return club_id
        return None
    
    @property
    def home_club(self) -> ClubStats:
        """Get the home club's stats."""
        club_id = self.home_club_id
        return self.clubs.get(club_id) if club_id else None
    
    @property
    def away_club(self) -> ClubStats:
        """Get the away club's stats."""
        club_id = self.away_club_id
        return self.clubs.get(club_id) if club_id else None
    
    @property
    def home_players(self) -> Dict[str, PlayerStats]:
        """Get all players from the home team."""
        club_id = self.home_club_id
        return self.players.get(club_id, {}) if club_id else {}
    
    @property
    def away_players(self) -> Dict[str, PlayerStats]:
        """Get all players from the away team."""
        club_id = self.away_club_id
        return self.players.get(club_id, {}) if club_id else {}
    
    @property
    def home_aggregate(self) -> AggregateStats:
        """Get aggregate stats for the home team."""
        club_id = self.home_club_id
        return self.aggregate.get(club_id) if club_id else None
    
    @property
    def away_aggregate(self) -> AggregateStats:
        """Get aggregate stats for the away team."""
        club_id = self.away_club_id
        return self.aggregate.get(club_id) if club_id else None
    
    def get_club_players(self, club_id: str) -> Dict[str, PlayerStats]:
        """
        Get all players for a specific club.
        
        Args:
            club_id: The ID of the club
            
        Returns:
            Dict mapping player IDs to their stats
        """
        return self.players.get(club_id, {})
    
    def get_player_stats(self, club_id: str, player_id: str) -> PlayerStats:
        """
        Get stats for a specific player.
        
        Args:
            club_id: The ID of the club
            player_id: The ID of the player
            
        Returns:
            PlayerStats if found, None otherwise
        """
        return self.players.get(club_id, {}).get(player_id)
    
    def get_club_aggregate(self, club_id: str) -> AggregateStats:
        """
        Get aggregate stats for a specific club.
        
        Args:
            club_id: The ID of the club
            
        Returns:
            AggregateStats if found, None otherwise
        """
        return self.aggregate.get(club_id) 