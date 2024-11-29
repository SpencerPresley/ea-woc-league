"""
Models for EA NHL player statistics.

This module provides models for player-level game statistics from the EA NHL API,
including both skater and goalie statistics.
"""

from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field, field_validator, computed_field


class PlayerStats(BaseModel):
    """
    Comprehensive player statistics for a single game.
    
    Contains all stats for both skater and goalie positions, along with
    general player and game information.
    """
    
    # Basic Information
    player_level: int = Field(alias="class")  # Player's level in the game
    position: str
    pos_sorted: int = Field(alias="posSorted")
    player_name: str = Field(alias="playername")
    client_platform: str = Field(alias="clientPlatform")
    player_level_display: int = Field(alias="playerLevel")  # Level shown in-game
    
    # Game Status
    is_guest: int = Field(alias="isGuest")
    player_dnf: int = Field(alias="player_dnf")
    pnhl_online_game_type: str = Field(alias="pNhlOnlineGameType")
    
    # Team Information
    team_id: int = Field(alias="teamId")
    team_side: int = Field(alias="teamSide")
    opponent_club_id: str = Field(alias="opponentClubId")
    opponent_team_id: int = Field(alias="opponentTeamId")
    opponent_score: int = Field(alias="opponentScore")
    score: int
    
    # Player Ratings
    rating_defense: float = Field(alias="ratingDefense")
    rating_offense: float = Field(alias="ratingOffense")
    rating_teamplay: float = Field(alias="ratingTeamplay")
    
    # Time Stats
    toi: int = Field(alias="toi")  # Time on ice (minutes)
    toi_seconds: int = Field(alias="toiseconds")  # Time on ice in seconds
    
    # Skater Stats
    skassists: int  # Assists
    skbs: int  # Blocked shots
    skdeflections: int  # Deflections
    skfol: int  # Faceoffs lost
    skfopct: float  # Faceoff percentage
    skfow: int  # Faceoffs won
    skgiveaways: int  # Giveaways
    skgoals: int  # Goals
    skgwg: int  # Game winning goals
    skhits: int  # Hits
    skinterceptions: int  # Interceptions
    skpassattempts: int  # Pass attempts
    skpasses: int  # Completed passes
    skpasspct: float  # Pass completion percentage
    skpenaltiesdrawn: int  # Penalties drawn
    skpim: int  # Penalty minutes
    skpkclearzone: int  # Penalty kill clear zone
    skplusmin: int  # Plus/minus
    skpossession: int  # Time in possession (seconds)
    skppg: int  # Power play goals
    sksaucerpasses: int  # Saucer passes
    skshg: int  # Short handed goals
    skshotattempts: int  # Shot attempts
    skshotonnetpct: float  # Shots on net percentage
    skshotpct: float  # Shooting percentage
    skshots: int  # Shots on goal
    sktakeaways: int  # Takeaways
    
    # Goalie Stats
    glbrksavepct: float  # Breakaway save percentage
    glbrksaves: int  # Breakaway saves
    glbrkshots: int  # Breakaway shots faced
    gldsaves: int  # Desperation saves
    glga: int  # Goals against
    glgaa: float  # Goals against average
    glpensavepct: float  # Penalty shot save percentage
    glpensaves: int  # Penalty shot saves
    glpenshots: int  # Penalty shots faced
    glpkclearzone: int  # Penalty kill clear zone
    glpokechecks: int  # Poke checks
    glsavepct: float  # Save percentage
    glsaves: int  # Total saves
    glshots: int  # Total shots faced
    glsoperiods: int  # Shutout periods

    # Field validators for string-to-numeric conversion
    @field_validator(
        'player_level', 'pos_sorted', 'player_level_display',
        'is_guest', 'player_dnf', 'team_id', 'team_side',
        'opponent_team_id', 'opponent_score', 'score',
        'toi', 'toi_seconds',
        'skassists', 'skbs', 'skdeflections', 'skfol', 'skfow',
        'skgiveaways', 'skgoals', 'skgwg', 'skhits', 'skinterceptions',
        'skpassattempts', 'skpasses', 'skpenaltiesdrawn', 'skpim',
        'skpkclearzone', 'skplusmin', 'skpossession', 'skppg',
        'sksaucerpasses', 'skshg', 'skshotattempts', 'skshots',
        'sktakeaways',
        'glbrksaves', 'glbrkshots', 'gldsaves', 'glga',
        'glpensaves', 'glpenshots', 'glpkclearzone', 'glpokechecks',
        'glsaves', 'glshots', 'glsoperiods',
        mode='before'
    )
    @classmethod
    def convert_to_int(cls, v):
        """Convert string values to integers."""
        return int(v) if isinstance(v, str) else v

    @field_validator(
        'rating_defense', 'rating_offense', 'rating_teamplay',
        'skfopct', 'skpasspct', 'skshotonnetpct', 'skshotpct',
        'glbrksavepct', 'glgaa', 'glpensavepct', 'glsavepct',
        mode='before'
    )
    @classmethod
    def convert_to_float(cls, v):
        """Convert string values to floats."""
        return float(v) if isinstance(v, str) else v

    # Computed properties
    @computed_field
    @property
    def points(self) -> int:
        """Total points (goals + assists)."""
        return self.skgoals + self.skassists

    @computed_field
    @property
    def faceoffs_total(self) -> int:
        """Total faceoffs taken."""
        return self.skfow + self.skfol

    @computed_field
    @property
    def faceoff_percentage(self) -> Optional[float]:
        """
        Faceoff win percentage.
        
        Returns:
            float: Percentage of faceoffs won (0-100)
            None: If no faceoffs were taken
        """
        total = self.faceoffs_total
        if total == 0:
            return None
        return round((self.skfow / total) * 100, 2)

    @computed_field
    @property
    def shots_missed(self) -> int:
        """Number of missed shots."""
        return max(0, self.skshotattempts - self.skshots)  # Ensure non-negative

    @computed_field
    @property
    def shooting_percentage(self) -> Optional[float]:
        """
        Shooting percentage (goals/shots).
        
        Returns:
            float: Percentage of shots that were goals (0-100)
            None: If no shots were taken
        """
        if self.skshots == 0:
            return None
        return round((self.skgoals / self.skshots) * 100, 2)

    @computed_field
    @property
    def passes_missed(self) -> int:
        """Number of incomplete passes."""
        return max(0, self.skpassattempts - self.skpasses)  # Ensure non-negative

    @computed_field
    @property
    def passing_percentage(self) -> Optional[float]:
        """
        Pass completion percentage.
        
        Returns:
            float: Percentage of passes completed (0-100)
            None: If no passes were attempted
        """
        if self.skpassattempts == 0:
            return None
        return round((self.skpasses / self.skpassattempts) * 100, 2)

    @computed_field
    @property
    def goals_saved(self) -> Optional[int]:
        """
        Total number of goals saved (goalie only).
        
        Returns:
            int: Number of saves if player is a goalie
            None: If player is not a goalie
        """
        if self.position != "goalie":
            return None
        return max(0, self.glshots - self.glga)  # Ensure non-negative

    @computed_field
    @property
    def save_percentage(self) -> Optional[float]:
        """
        Save percentage for goalies.
        
        Returns:
            float: Percentage of shots saved (0-100)
            None: If not a goalie or no shots faced
        """
        if self.position != "goalie" or self.glshots == 0:
            return None
        return round((self.glsaves / self.glshots) * 100, 2)

    @computed_field
    @property
    def major_penalties(self) -> int:
        """Number of major penalties (5 minutes each)."""
        return self.skpim // 5

    @computed_field
    @property
    def minor_penalties(self) -> int:
        """Number of minor penalties (2 minutes each)."""
        return (self.skpim % 5) // 2

    @computed_field
    @property
    def total_penalties(self) -> int:
        """Total number of penalties taken."""
        return self.major_penalties + self.minor_penalties

    @computed_field
    @property
    def points_per_60(self) -> float:
        """Points per 60 minutes of ice time."""
        return round((self.points * 60) / self.toi, 2) if self.toi > 0 else 0.0

    @computed_field
    @property
    def possession_per_minute(self) -> float:
        """Time in possession per minute of ice time."""
        return round(self.skpossession / self.toi, 2) if self.toi > 0 else 0.0

    @computed_field
    @property
    def shot_efficiency(self) -> Optional[float]:
        """
        Shooting efficiency considering all shot attempts.
        More punishing than regular shooting percentage as it includes missed shots.
        
        Returns:
            float: Percentage of shot attempts that were goals (0-100)
            None: If no shot attempts
        """
        if self.skshotattempts == 0:
            return None
        return round((self.skgoals / self.skshotattempts) * 100, 2)

    @computed_field
    @property
    def takeaway_giveaway_ratio(self) -> Optional[float]:
        """
        Ratio of takeaways to giveaways.
        
        Returns:
            float: Ratio of takeaways to giveaways (> 1 is good)
            None: If no giveaways
        """
        if self.skgiveaways == 0:
            return None
        return round(self.sktakeaways / self.skgiveaways, 2)

    @computed_field
    @property
    def penalty_differential(self) -> int:
        """Net penalties (drawn - taken)."""
        return self.skpenaltiesdrawn - self.total_penalties

    @computed_field
    @property
    def defensive_actions_per_minute(self) -> float:
        """
        Number of defensive actions (hits, blocks, takeaways) per minute.
        Useful for comparing defensive activity level regardless of TOI.
        """
        if self.toi == 0:
            return 0.0
        actions = self.skhits + self.skbs + self.sktakeaways
        return round(actions / self.toi, 2)

    @computed_field
    @property
    def offensive_impact(self) -> float:
        """
        Offensive impact per minute considering goals, assists, and shots.
        Useful for comparing offensive contribution regardless of TOI.
        """
        if self.toi == 0:
            return 0.0
        impact = (self.skgoals * 2) + self.skassists + (self.skshots * 0.5)
        return round(impact / self.toi, 2)

    @computed_field
    @property
    def defensive_impact(self) -> float:
        """
        Defensive impact per minute.
        Positive actions (hits, blocks, takeaways) minus negative (giveaways).
        """
        if self.toi == 0:
            return 0.0
        impact = (self.skhits + self.skbs + self.sktakeaways) - self.skgiveaways
        return round(impact / self.toi, 2)
    