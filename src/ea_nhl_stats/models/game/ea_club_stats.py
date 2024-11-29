"""
Models for EA NHL club statistics.

This module provides models for club-level game statistics, including both
individual club stats and aggregate team stats from the EA NHL API.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class CustomKit(BaseModel):
    """Custom team kit configuration data."""

    is_custom_team: int = Field(alias="isCustomTeam")
    crest_asset_id: str = Field(alias="crestAssetId")
    use_base_asset: int = Field(alias="useBaseAsset")

    @field_validator('is_custom_team', 'use_base_asset', mode='before')
    @classmethod
    def convert_to_int(cls, v):
        """Convert string values to integers."""
        return int(v) if isinstance(v, str) else v


class ClubDetails(BaseModel):
    """Club details including identification and customization information."""

    name: str
    club_id: int = Field(alias="clubId")
    region_id: int = Field(alias="regionId")
    team_id: int = Field(alias="teamId")
    custom_kit: CustomKit = Field(alias="customKit")

    @field_validator('club_id', 'region_id', 'team_id', mode='before')
    @classmethod
    def convert_to_int(cls, v):
        """Convert string values to integers."""
        return int(v) if isinstance(v, str) else v


class ClubStats(BaseModel):
    """
    Club-level game statistics and information.
    
    Contains team performance metrics, scores, and general game outcomes.
    """
    
    # Basic Information
    club_division: int = Field(alias="clubDivision")
    cnhl_online_game_type: str = Field(alias="cNhlOnlineGameType")
    
    # Game Results
    goals_against_raw: int = Field(alias="garaw")
    goals_for_raw: int = Field(alias="gfraw")
    losses: int
    result: int
    score: int
    score_string: str = Field(alias="scoreString")
    winner_by_dnf: int = Field(alias="winnerByDnf")
    winner_by_goalie_dnf: int = Field(alias="winnerByGoalieDnf")
    
    # Team Stats
    member_string: str = Field(alias="memberString")
    passes_attempted: int = Field(alias="passa")
    passes_completed: int = Field(alias="passc")
    powerplay_goals: int = Field(alias="ppg")
    powerplay_opportunities: int = Field(alias="ppo")
    shots: int
    team_art_abbr: str = Field(alias="teamArtAbbr")
    team_side: int = Field(alias="teamSide")
    time_on_attack: int = Field(alias="toa")
    
    # Opponent Info
    opponent_club_id: str = Field(alias="opponentClubId")
    opponent_score: int = Field(alias="opponentScore")
    opponent_team_art_abbr: str = Field(alias="opponentTeamArtAbbr")
    
    # Club Details
    details: ClubDetails
    goals: int
    goals_against: int = Field(alias="goalsAgainst")

    @field_validator(
        'club_division', 'goals_against_raw', 'goals_for_raw', 'losses',
        'result', 'score', 'passes_attempted', 'passes_completed',
        'powerplay_goals', 'powerplay_opportunities', 'shots',
        'team_side', 'time_on_attack', 'opponent_score', 'goals',
        'goals_against', 'winner_by_dnf', 'winner_by_goalie_dnf',
        mode='before'
    )
    @classmethod
    def convert_to_int(cls, v):
        """Convert string values to integers."""
        return int(v) if isinstance(v, str) else v


class AggregateStats(BaseModel):
    """
    Aggregate team statistics for a game.
    
    Contains combined stats for all players on the team.
    """
    
    # Basic Information
    club_level: int = Field(alias="class")  # The club's level in the game
    position: int  # TODO: Document purpose of this field
    pos_sorted: int = Field(alias="posSorted")  # TODO: Document purpose of this field
    
    # Game Status
    is_guest: int = Field(alias="isGuest")
    player_dnf: int = Field(alias="player_dnf")
    player_level: int = Field(alias="playerLevel")  # TODO: Document why this is in aggregate stats
    
    # Team Information
    team_id: int = Field(alias="teamId")
    team_side: int = Field(alias="teamSide")
    opponent_club_id: int = Field(alias="opponentClubId")
    opponent_team_id: int = Field(alias="opponentTeamId")
    opponent_score: int = Field(alias="opponentScore")
    
    # Game Results
    score: int
    
    # Team Ratings
    rating_defense: float = Field(alias="ratingDefense")
    rating_offense: float = Field(alias="ratingOffense")
    rating_teamplay: float = Field(alias="ratingTeamplay")
    
    # Time Stats
    toi: int = Field(alias="toi")
    toi_seconds: int = Field(alias="toiseconds")
    
    # Skater Stats
    skassists: int
    skbs: int  # Blocked shots
    skdeflections: int
    skfol: int  # Faceoffs lost
    skfopct: float  # Faceoff percentage
    skfow: int  # Faceoffs won
    skgiveaways: int
    skgoals: int
    skgwg: int  # Game winning goals
    skhits: int
    skinterceptions: int
    skpassattempts: int
    skpasses: int
    skpasspct: float
    skpenaltiesdrawn: int
    skpim: int  # Penalty minutes
    skpkclearzone: int  # Penalty kill clear zone
    skplusmin: int  # Plus/minus
    skpossession: int
    skppg: int  # Power play goals
    sksaucerpasses: int
    skshg: int  # Short handed goals
    skshotattempts: int
    skshotonnetpct: float
    skshotpct: float
    skshots: int
    sktakeaways: int
    
    # Goalie Stats
    glbrksavepct: float  # Breakaway save percentage
    glbrksaves: int  # Breakaway saves
    glbrkshots: int  # Breakaway shots
    gldsaves: int  # Desperation saves
    glga: int  # Goals against
    glgaa: float  # Goals against average
    glpensavepct: float  # Penalty shot save percentage
    glpensaves: int  # Penalty shot saves
    glpenshots: int  # Penalty shots
    glpkclearzone: int  # Penalty kill clear zone
    glpokechecks: int
    glsavepct: float  # Save percentage
    glsaves: int
    glshots: int
    glsoperiods: int  # Shutout periods

    @field_validator(
        'club_level', 'is_guest', 'player_dnf', 'player_level',
        'position', 'pos_sorted', 'team_id', 'team_side',
        'opponent_club_id', 'opponent_score', 'opponent_team_id',
        'score', 'toi', 'toi_seconds', 'skassists', 'skbs',
        'skdeflections', 'skfol', 'skfow', 'skgiveaways',
        'skgoals', 'skgwg', 'skhits', 'skinterceptions',
        'skpassattempts', 'skpasses', 'skpenaltiesdrawn',
        'skpim', 'skpkclearzone', 'skplusmin', 'skpossession',
        'skppg', 'sksaucerpasses', 'skshg', 'skshotattempts',
        'skshots', 'sktakeaways', 'glbrksaves', 'glbrkshots',
        'gldsaves', 'glga', 'glpensaves', 'glpenshots',
        'glpkclearzone', 'glpokechecks', 'glsaves', 'glshots',
        'glsoperiods',
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


class Club(BaseModel):
    """
    Complete club data including stats and aggregates.
    
    This model combines both the club-level statistics and the aggregate
    team statistics for a complete view of the club's performance.
    """
    
    stats: ClubStats
    aggregate: AggregateStats