"""Models for tracking player history and statistics across seasons.

This module defines models for tracking player statistics and match history
across multiple seasons. It provides functionality for aggregating player
performance metrics and maintaining detailed match records.
"""

from typing import Dict, Set
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from ea_nhl_stats.league.enums.types import Position
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats


class SeasonStats(BaseModel):
    """Statistics for a player in a single season.
    
    This class maintains both game-by-game statistics and season aggregates
    for a player. It serves as a container for all statistical data within
    a single season.
    """
    
    # Season identification
    season: int = Field(
        gt=0,  # Must be positive
        description="Season number these stats are for"
    )
    
    # Game tracking
    games_played: int = Field(
        default=0,
        ge=0,  # Cannot be negative
        description="Number of games played in the season"
    )
    game_stats: Dict[str, PlayerStats] = Field(
        default_factory=dict,
        description="Stats for each game, keyed by match ID"
    )
    
    # Position tracking
    positions: Set[Position] = Field(
        default_factory=set,
        description="Positions played during the season"
    )
    
    @computed_field
    @property
    def goals(self) -> int:
        """Total goals scored in the season."""
        return sum(stats.skgoals for stats in self.game_stats.values())
    
    @computed_field
    @property
    def assists(self) -> int:
        """Total assists in the season."""
        return sum(stats.skassists for stats in self.game_stats.values())
    
    @computed_field
    @property
    def points(self) -> int:
        """Total points (goals + assists) in the season."""
        return self.goals + self.assists
    
    @computed_field
    @property
    def shots(self) -> int:
        """Total shots taken in the season."""
        return sum(stats.skshots for stats in self.game_stats.values())
    
    @computed_field
    @property
    def hits(self) -> int:
        """Total hits delivered in the season."""
        return sum(stats.skhits for stats in self.game_stats.values())
    
    @computed_field
    @property
    def takeaways(self) -> int:
        """Total takeaways in the season."""
        return sum(stats.sktakeaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def giveaways(self) -> int:
        """Total giveaways in the season."""
        return sum(stats.skgiveaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def penalty_minutes(self) -> int:
        """Total penalty minutes in the season."""
        return sum(stats.skpim for stats in self.game_stats.values())
    
    @computed_field
    @property
    def plus_minus(self) -> int:
        """Total plus/minus in the season."""
        return sum(stats.skplusmin for stats in self.game_stats.values())
    
    @computed_field
    @property
    def shooting_percentage(self) -> float:
        """Shooting percentage for the season."""
        if self.shots == 0:
            return 0.0
        return round((self.goals / self.shots) * 100, 2)
    
    @computed_field
    @property
    def points_per_game(self) -> float:
        """Points per game for the season."""
        if self.games_played == 0:
            return 0.0
        return round(self.points / self.games_played, 2)
    
    @computed_field
    @property
    def takeaway_giveaway_ratio(self) -> float:
        """Ratio of takeaways to giveaways."""
        if self.giveaways == 0:
            return 0.0
        return round(self.takeaways / self.giveaways, 2)