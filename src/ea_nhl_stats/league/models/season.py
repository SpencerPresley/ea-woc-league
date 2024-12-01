"""Season container model.

This module provides the Season model which acts as a container for organizing
league data by season. Each season maintains its own instances of teams and
players organized by tier.
"""
from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer
from ea_nhl_stats.league.factories.team_factory import TeamFactory
from ea_nhl_stats.league.models.teams.implementations import *  # noqa: F403


class LeagueData(BaseModel):
    """Container for all league data across multiple seasons.
    
    This model represents the complete league data structure, containing all seasons
    and their associated data.
    
    Attributes:
        seasons: Dictionary mapping season keys to Season instances
    """
    
    seasons: Dict[str, Season] = Field(
        default_factory=dict,
        description="All seasons in the league, keyed by season_{season_id}"
    )


class TierData(BaseModel):
    """Container for tier-specific data within a season.
    
    This model organizes teams and players for a specific tier (NHL/AHL/ECHL)
    within a season. Each tier maintains its own set of team and player instances.
    
    Attributes:
        teams: Dictionary mapping team identifiers to team instances
        players: Dictionary mapping player UUIDs to player instances
    """
    
    teams: Dict[TeamIdentifier, LeagueTeam] = Field(
        default_factory=dict,
        description="Teams in this tier for this season"
    )
    players: Dict[UUID, LeaguePlayer] = Field(
        default_factory=dict,
        description="Players who played in this tier during this season"
    )


class Season(BaseModel):
    """Container for organizing league data by season.
    
    This model acts as a pure container, organizing teams and players by tier
    for a specific season. Each season maintains its own instances of teams
    and players, ensuring data isolation between seasons.
    
    The structure is:
    {
        LeagueLevel.NHL: {
            teams: {TeamIdentifier: LeagueTeam},
            players: {UUID: LeaguePlayer}
        },
        LeagueLevel.AHL: {...},
        LeagueLevel.ECHL: {...}
    }
    
    Attributes:
        season_id: Unique identifier for this season
        tiers: Dictionary mapping league levels to their data
    """
    
    season_id: str = Field(description="Unique identifier for this season")
    tiers: Dict[LeagueLevel, TierData] = Field(
        default_factory=dict,
        description="Data for each tier in this season"
    )
    
    def get_team(self, tier: LeagueLevel, team_id: TeamIdentifier) -> LeagueTeam:
        """Get a team instance from this season.
        
        Args:
            tier: The league level to look in
            team_id: The team identifier to find
            
        Returns:
            The team instance if found
            
        Raises:
            KeyError: If team not found in this tier
        """
        return self.tiers[tier].teams[team_id]
    
    def get_player(self, tier: LeagueLevel, player_id: UUID) -> LeaguePlayer:
        """Get a player instance from this season.
        
        Args:
            tier: The league level to look in
            player_id: The player's UUID
            
        Returns:
            The player instance if found
            
        Raises:
            KeyError: If player not found in this tier
        """
        return self.tiers[tier].players[player_id]
    
    def add_team(self, tier: LeagueLevel, team_id: TeamIdentifier, team: LeagueTeam) -> None:
        """Add a team to this season.
        
        Args:
            tier: The league level to add to
            team_id: The team identifier
            team: The team instance
        """
        self.tiers[tier].teams[team_id] = team
    
    def add_player(self, tier: LeagueLevel, player_id: UUID, player: LeaguePlayer) -> None:
        """Add a player to this season.
        
        Args:
            tier: The league level to add to
            player_id: The player's UUID
            player: The player instance
        """
        self.tiers[tier].players[player_id] = player


class SeasonBuilder:
    """Builder for creating properly initialized Season instances.
    
    This builder ensures that seasons are created with the correct teams
    for each tier based on the registered team implementations.
    """
    
    def __init__(self) -> None:
        """Initialize a new SeasonBuilder."""
        self._season_id: Optional[str] = None
        self._tiers: Dict[LeagueLevel, TierData] = {}
    
    def with_season_id(self, season_id: str) -> 'SeasonBuilder':
        """Set the season ID.
        
        Args:
            season_id: Unique identifier for the season
            
        Returns:
            Self for method chaining
        """
        self._season_id = season_id
        return self
    
    def with_tier(self, tier: LeagueLevel) -> 'SeasonBuilder':
        """Add a tier with its registered teams.
        
        This method creates a new TierData instance for the specified tier
        and initializes it with all registered teams for that tier.
        
        Args:
            tier: The league level to add
            
        Returns:
            Self for method chaining
        """
        tier_data = TierData()
        
        # Get all registered teams for this tier
        for team_id in TeamIdentifier:
            try:
                # Create new team instance for this season
                team = TeamFactory.create(team_id)
                if team.league_level == tier:
                    tier_data.teams[team_id] = team
            except ValueError:
                # Skip if team implementation doesn't exist
                continue
        
        self._tiers[tier] = tier_data
        return self
    
    def build(self) -> Season:
        """Build the Season instance.
        
        Returns:
            Properly initialized Season instance
            
        Raises:
            ValueError: If season_id not set
        """
        if not self._season_id:
            raise ValueError("Season ID must be set")
            
        # Create new instances of teams for this season
        season_tiers: Dict[LeagueLevel, TierData] = {}
        for tier_level, tier_data in self._tiers.items():
            new_tier = TierData()
            
            # Create new instances of teams
            for team_id in tier_data.teams:
                new_tier.teams[team_id] = TeamFactory.create(team_id)
            
            season_tiers[tier_level] = new_tier
            
        return Season(
            season_id=self._season_id,
            tiers=season_tiers
        )
