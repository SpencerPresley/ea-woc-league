"""
Models for NHL club and match data.

This module provides models for representing club information and match details.
"""

from typing import Dict

from pydantic import Field

from ea_nhl_stats.models.game.base import NumericValidatorBase
from ea_nhl_stats.models.game.player import PlayerStats, AggregateStats


# Type aliases for complex nested structures
ClubDict = Dict[str, "Club"]
"""A dictionary where the key is a string and the value is a Club object."""

PlayerStatsDict = Dict[str, Dict[str, PlayerStats]]
"""A dictionary where the key is a string and the value is a dictionary of player stats."""

AggregateStatsDict = Dict[str, AggregateStats]
"""A dictionary where the key is a string and the value is an AggregateStats object."""


class CustomKit(NumericValidatorBase):
    """Custom team kit configuration data."""

    is_custom_team: int = Field(alias="isCustomTeam")
    crest_asset_id: str = Field(alias="crestAssetId")
    use_base_asset: int = Field(alias="useBaseAsset")


class Details(NumericValidatorBase):
    """Club details including identification and customization information."""

    name: str
    club_id: int = Field(alias="clubId")
    region_id: int = Field(alias="regionId")
    team_id: int = Field(alias="teamId")
    custom_kit: CustomKit = Field(alias="customKit")


class Club(NumericValidatorBase):
    """
    Club-level game statistics and information.
    
    Contains team performance metrics, scores, and general game outcomes.
    """
    
    # Basic Information
    club_division: str = Field(alias="clubDivision")
    club_name: str = Field(alias="clubname", default="")
    
    # Game Type
    cnhl_online_game_type: str = Field(alias="cNhlOnlineGameType")
    
    # Game Results
    goals_against_raw: str = Field(alias="garaw")
    goals_for_raw: str = Field(alias="gfraw")
    losses: str
    result: str
    score: str
    score_string: str = Field(alias="scoreString")
    winner_by_dnf: str = Field(alias="winnerByDnf")
    winner_by_goalie_dnf: str = Field(alias="winnerByGoalieDnf")
    
    # Team Stats
    member_string: str = Field(alias="memberString")
    passes_attempted: str = Field(alias="passa")
    passes_completed: str = Field(alias="passc")
    powerplay_goals: str = Field(alias="ppg")
    powerplay_opportunities: str = Field(alias="ppo")
    shots: str
    team_art_abbr: str = Field(alias="teamArtAbbr")
    team_side: str = Field(alias="teamSide")
    time_on_attack: str = Field(alias="toa")
    
    # Opponent Info
    opponent_club_id: str = Field(alias="opponentClubId")
    opponent_score: str = Field(alias="opponentScore")
    opponent_team_art_abbr: str = Field(alias="opponentTeamArtAbbr")
    
    # Club Details
    details: Details
    goals: str
    goals_against: str = Field(alias="goalsAgainst")


class TimeAgo(NumericValidatorBase):
    """Time elapsed since the match."""
    
    number: int
    unit: str


class Match(NumericValidatorBase):
    """
    Complete match data including all clubs and players.
    
    Contains detailed statistics for each club and player involved in the match.
    """
    
    match_id: str = Field(alias="matchId")
    timestamp: int
    time_ago: TimeAgo = Field(alias="timeAgo")
    clubs: ClubDict
    players: PlayerStatsDict
    aggregate: AggregateStatsDict