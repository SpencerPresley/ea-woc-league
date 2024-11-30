"""Models for tracking player history and statistics.

This module defines models for tracking player statistics and match history.
It provides functionality for aggregating player performance metrics and
maintaining detailed match records.
"""

from typing import Dict, Set
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from ea_nhl_stats.league.enums.types import Position
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats as EAPlayerStats


class PlayerStats(BaseModel):
    """Statistics for a player.
    
    This class maintains both game-by-game statistics and aggregates
    for a player. It serves as a container for all statistical data.
    """
    
    # Game tracking
    games_played: int = Field(
        default=0,
        ge=0,  # Cannot be negative
        description="Number of games played"
    )
    game_stats: Dict[UUID, EAPlayerStats] = Field(
        default_factory=dict,
        description="Stats for each game, keyed by match ID"
    )
    
    # Position tracking
    positions: Set[Position] = Field(
        default_factory=set,
        description="Positions played"
    )
    
    @computed_field
    @property
    def goals(self) -> int:
        """Total goals scored."""
        return sum(stats.skgoals for stats in self.game_stats.values())
    
    @computed_field
    @property
    def assists(self) -> int:
        """Total assists."""
        return sum(stats.skassists for stats in self.game_stats.values())
    
    @computed_field
    @property
    def points(self) -> int:
        """Total points (goals + assists)."""
        return self.goals + self.assists
    
    @computed_field
    @property
    def shots(self) -> int:
        """Total shots taken."""
        return sum(stats.skshots for stats in self.game_stats.values())
    
    @computed_field
    @property
    def hits(self) -> int:
        """Total hits delivered."""
        return sum(stats.skhits for stats in self.game_stats.values())
    
    @computed_field
    @property
    def takeaways(self) -> int:
        """Total takeaways."""
        return sum(stats.sktakeaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def giveaways(self) -> int:
        """Total giveaways."""
        return sum(stats.skgiveaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def penalty_minutes(self) -> int:
        """Total penalty minutes."""
        return sum(stats.skpim for stats in self.game_stats.values())
    
    @computed_field
    @property
    def plus_minus(self) -> int:
        """Total plus/minus."""
        return sum(stats.skplusmin for stats in self.game_stats.values())
    
    @computed_field
    @property
    def shooting_percentage(self) -> float:
        """Shooting percentage."""
        if self.shots == 0:
            return 0.0
        return round((self.goals / self.shots) * 100, 2)
    
    @computed_field
    @property
    def points_per_game(self) -> float:
        """Points per game."""
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