"""Models for tracking team statistics.

This module defines models for tracking team statistics and match history.
It provides functionality for aggregating team performance metrics and
maintaining detailed match records.
"""

from typing import Dict
from pydantic import BaseModel, Field, computed_field

from ea_nhl_stats.models.game.ea_club_stats import ClubStats


class TeamStats(BaseModel):
    """Statistics for a team.
    
    This class maintains both match-by-match statistics and aggregates
    for a team. It serves as a container for all statistical data.
    
    Attributes:
        matches_played: Total number of matches played
        matches: Dictionary of match statistics, keyed by match ID
        wins: Total wins
        losses: Total losses
        goals_for: Total goals scored
        goals_against: Total goals against
        shots: Total shots taken
        shots_against: Total shots against
        powerplay_goals: Total powerplay goals
        powerplay_opportunities: Total powerplay opportunities
        penalty_kill_goals_against: Total goals against while shorthanded
        penalty_kill_opportunities: Total times shorthanded
        time_on_attack: Total time on attack (in seconds)
    """
    
    # Match tracking
    matches_played: int = Field(
        default=0,
        ge=0,  # Cannot be negative
        description="Number of matches played"
    )
    matches: Dict[str, ClubStats] = Field(
        default_factory=dict,
        description="Stats for each match, keyed by match ID"
    )
    
    # Core stats
    wins: int = Field(
        default=0,
        ge=0,
        description="Total wins"
    )
    losses: int = Field(
        default=0,
        ge=0,
        description="Total losses"
    )
    goals_for: int = Field(
        default=0,
        ge=0,
        description="Total goals scored"
    )
    goals_against: int = Field(
        default=0,
        ge=0,
        description="Total goals against"
    )
    shots: int = Field(
        default=0,
        ge=0,
        description="Total shots taken"
    )
    shots_against: int = Field(
        default=0,
        ge=0,
        description="Total shots against"
    )
    
    # Special teams
    powerplay_goals: int = Field(
        default=0,
        ge=0,
        description="Total powerplay goals"
    )
    powerplay_opportunities: int = Field(
        default=0,
        ge=0,
        description="Total powerplay opportunities"
    )
    penalty_kill_goals_against: int = Field(
        default=0,
        ge=0,
        description="Total goals against while shorthanded"
    )
    penalty_kill_opportunities: int = Field(
        default=0,
        ge=0,
        description="Total times shorthanded"
    )
    
    # Time stats
    time_on_attack: int = Field(
        default=0,
        ge=0,
        description="Total time on attack (seconds)"
    )
    
    def add_match(self, match_id: str, stats: ClubStats) -> None:
        """Add statistics from a single match.
        
        This method processes match statistics and updates totals.
        
        Args:
            match_id: Unique identifier for the match
            stats: Statistics from the match
            
        Note:
            This method automatically updates all totals.
        """
        # Store match stats
        self.matches[match_id] = stats
        self.matches_played += 1
        
        # Update core stats
        if stats.goals > stats.goals_against:
            self.wins += 1
        else:
            self.losses += 1
            
        self.goals_for += stats.goals
        self.goals_against += stats.goals_against
        self.shots += stats.shots
        self.powerplay_goals += stats.powerplay_goals
        self.powerplay_opportunities += stats.powerplay_opportunities
        self.time_on_attack += stats.time_on_attack
    
    @computed_field
    @property
    def points(self) -> int:
        """Total points (2 for win, 0 for loss)."""
        return self.wins * 2
    
    @computed_field
    @property
    def win_percentage(self) -> float:
        """Win percentage."""
        if self.matches_played == 0:
            return 0.0
        return round((self.wins / self.matches_played) * 100, 2)
    
    @computed_field
    @property
    def goals_per_game(self) -> float:
        """Average goals scored per game."""
        if self.matches_played == 0:
            return 0.0
        return round(self.goals_for / self.matches_played, 2)
    
    @computed_field
    @property
    def goals_against_per_game(self) -> float:
        """Average goals against per game."""
        if self.matches_played == 0:
            return 0.0
        return round(self.goals_against / self.matches_played, 2)
    
    @computed_field
    @property
    def goal_differential(self) -> int:
        """Total goal differential (goals for - goals against)."""
        return self.goals_for - self.goals_against
    
    @computed_field
    @property
    def shooting_percentage(self) -> float:
        """Team shooting percentage."""
        if self.shots == 0:
            return 0.0
        return round((self.goals_for / self.shots) * 100, 2)
    
    @computed_field
    @property
    def powerplay_percentage(self) -> float:
        """Powerplay success percentage."""
        if self.powerplay_opportunities == 0:
            return 0.0
        return round((self.powerplay_goals / self.powerplay_opportunities) * 100, 2)
    
    @computed_field
    @property
    def penalty_kill_percentage(self) -> float:
        """Penalty kill success percentage."""
        if self.penalty_kill_opportunities == 0:
            return 100.0
        goals_prevented = self.penalty_kill_opportunities - self.penalty_kill_goals_against
        return round((goals_prevented / self.penalty_kill_opportunities) * 100, 2)
    
    @computed_field
    @property
    def time_on_attack_per_game(self) -> float:
        """Average time on attack per game (in seconds)."""
        if self.matches_played == 0:
            return 0.0
        return round(self.time_on_attack / self.matches_played, 2)
    