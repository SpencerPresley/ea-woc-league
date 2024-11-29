"""
Models for NHL player statistics.

This module provides models for representing individual player statistics,
including both skater and goalie stats.
"""

from typing import Optional

from pydantic import Field

from ea_nhl_stats.models.game.base import NumericValidatorBase


class PlayerStats(NumericValidatorBase):
    """
    Comprehensive player statistics for a single game.
    
    Includes goalie stats (gl prefix), skater stats (sk prefix), and general game information.
    """
    
    # Basic Information
    class_: int = Field(alias="class")
    position: str
    pos_sorted: int = Field(alias="posSorted")
    player_name: str = Field(alias="playername")
    client_platform: str = Field(alias="clientPlatform")
    player_level: int = Field(alias="playerLevel")
    
    # Game Status
    is_guest: int = Field(alias="isGuest")
    member_string: str = Field(alias="memberString")
    player_dnf: int = Field(alias="player_dnf")
    removed_reason: int = Field(alias="removedReason")
    
    # Team Information
    team_id: int = Field(alias="teamId")
    team_side: int = Field(alias="teamSide")
    team_art_abbr: str = Field(alias="teamArtAbbr")
    opponent_club_id: int = Field(alias="opponentClubId")
    opponent_team_id: int = Field(alias="opponentTeamId")
    opponent_team_art_abbr: str = Field(alias="opponentTeamArtAbbr")
    
    # Game Results
    result: int
    score: int
    score_raw: int = Field(alias="scoreRaw")
    score_string: str = Field(alias="scoreString")
    opponent_score: int = Field(alias="opponentScore")
    
    # Player Ratings
    rank_points: Optional[int] = Field(alias="rankpoints", default=None)
    rank_tier_asset_id: int = Field(alias="ranktierassetid")
    rating_defense: float = Field(alias="ratingDefense")
    rating_offense: float = Field(alias="ratingOffense")
    rating_teamplay: float = Field(alias="ratingTeamplay")
    
    # Time Stats
    toi: int = Field(alias="toi")
    toi_seconds: int = Field(alias="toiseconds")
    
    # Skater Stats
    sk_assists: int = Field(alias="skassists")
    sk_blocked_shots: int = Field(alias="skbs")
    sk_deflections: int = Field(alias="skdeflections")
    sk_faceoffs_lost: int = Field(alias="skfol")
    sk_faceoff_pct: float = Field(alias="skfopct")
    sk_faceoffs_won: int = Field(alias="skfow")
    sk_giveaways: int = Field(alias="skgiveaways")
    sk_goals: int = Field(alias="skgoals")
    sk_game_winning_goals: int = Field(alias="skgwg")
    sk_hits: int = Field(alias="skhits")
    sk_interceptions: int = Field(alias="skinterceptions")
    sk_pass_attempts: int = Field(alias="skpassattempts")
    sk_passes: int = Field(alias="skpasses")
    sk_pass_pct: float = Field(alias="skpasspct")
    sk_penalties_drawn: int = Field(alias="skpenaltiesdrawn")
    sk_penalty_minutes: int = Field(alias="skpim")
    sk_pk_clearzone: int = Field(alias="skpkclearzone")
    sk_plus_minus: int = Field(alias="skplusmin")
    sk_possession: int = Field(alias="skpossession")
    sk_powerplay_goals: int = Field(alias="skppg")
    sk_saucer_passes: int = Field(alias="sksaucerpasses")
    sk_short_handed_goals: int = Field(alias="skshg")
    sk_shot_attempts: int = Field(alias="skshotattempts")
    sk_shot_on_net_pct: float = Field(alias="skshotonnetpct")
    sk_shot_pct: float = Field(alias="skshotpct")
    sk_shots: int = Field(alias="skshots")
    sk_takeaways: int = Field(alias="sktakeaways")
    
    # Goalie Stats
    gl_breakaway_save_pct: float = Field(alias="glbrksavepct")
    gl_breakaway_saves: int = Field(alias="glbrksaves")
    gl_breakaway_shots: int = Field(alias="glbrkshots")
    gl_desperation_saves: int = Field(alias="gldsaves")
    gl_goals_against: int = Field(alias="glga")
    gl_goals_against_avg: float = Field(alias="glgaa")
    gl_penalty_save_pct: float = Field(alias="glpensavepct")
    gl_penalty_saves: int = Field(alias="glpensaves")
    gl_penalty_shots: int = Field(alias="glpenshots")
    gl_pk_clearzone: int = Field(alias="glpkclearzone")
    gl_pokechecks: int = Field(alias="glpokechecks")
    gl_save_pct: float = Field(alias="glsavepct")
    gl_saves: int = Field(alias="glsaves")
    gl_shots: int = Field(alias="glshots")
    gl_shutout_periods: int = Field(alias="glsoperiods")


class AggregateStats(NumericValidatorBase):
    """
    Aggregate statistics for a team or player across multiple games.
    
    Similar structure to PlayerStats but represents cumulative values.
    """
    
    class_: int = Field(alias="class")
    gl_breakaway_save_pct: float = Field(alias="glbrksavepct")
    gl_breakaway_saves: int = Field(alias="glbrksaves")
    gl_breakaway_shots: int = Field(alias="glbrkshots")
    gl_desperation_saves: int = Field(alias="gldsaves")
    gl_goals_against: int = Field(alias="glga")
    gl_goals_against_avg: float = Field(alias="glgaa")
    gl_penalty_save_pct: float = Field(alias="glpensavepct")
    gl_penalty_saves: int = Field(alias="glpensaves")
    gl_penalty_shots: int = Field(alias="glpenshots")
    gl_pk_clearzone: int = Field(alias="glpkclearzone")
    gl_pokechecks: int = Field(alias="glpokechecks")
    gl_save_pct: float = Field(alias="glsavepct")
    gl_saves: int = Field(alias="glsaves")
    gl_shots: int = Field(alias="glshots")
    gl_shutout_periods: int = Field(alias="glsoperiods")
    is_guest: int = Field(alias="isGuest")
    member_string: str = Field(alias="memberString")
    opponent_club_id: int = Field(alias="opponentClubId")
    opponent_score: int = Field(alias="opponentScore")
    opponent_team_art_abbr: str = Field(alias="opponentTeamArtAbbr")
    opponent_team_id: int = Field(alias="opponentTeamId")
    player_dnf: int = Field(alias="player_dnf")
    player_level: int = Field(alias="playerLevel")
    p_nhl_online_game_type: int = Field(alias="pNhlOnlineGameType")
    position: str = Field(alias="position")
    pos_sorted: int = Field(alias="posSorted")
    rank_points: Optional[int] = Field(alias="rankpoints", default=None)
    rank_tier_asset_id: int = Field(alias="ranktierassetid")
    rating_defense: float = Field(alias="ratingDefense")
    rating_offense: float = Field(alias="ratingOffense")
    rating_teamplay: float = Field(alias="ratingTeamplay")
    removed_reason: int = Field(alias="removedReason")
    result: int = Field(alias="result")
    score: int = Field(alias="score")
    score_raw: int = Field(alias="scoreRaw")
    score_string: str = Field(alias="scoreString")
    sk_assists: int = Field(alias="skassists")
    sk_blocked_shots: int = Field(alias="skbs")
    sk_deflections: int = Field(alias="skdeflections")
    sk_faceoffs_lost: int = Field(alias="skfol")
    sk_faceoff_pct: float = Field(alias="skfopct")
    sk_faceoffs_won: int = Field(alias="skfow")
    sk_giveaways: int = Field(alias="skgiveaways")
    sk_goals: int = Field(alias="skgoals")
    sk_game_winning_goals: int = Field(alias="skgwg")
    sk_hits: int = Field(alias="skhits")
    sk_interceptions: int = Field(alias="skinterceptions")
    sk_pass_attempts: int = Field(alias="skpassattempts")
    sk_passes: int = Field(alias="skpasses")
    sk_pass_pct: float = Field(alias="skpasspct")
    sk_penalties_drawn: int = Field(alias="skpenaltiesdrawn")
    sk_penalty_minutes: int = Field(alias="skpim")
    sk_pk_clearzone: int = Field(alias="skpkclearzone")
    sk_plus_minus: int = Field(alias="skplusmin")
    sk_possession: int = Field(alias="skpossession")
    sk_powerplay_goals: int = Field(alias="skppg")
    sk_saucer_passes: int = Field(alias="sksaucerpasses")
    sk_short_handed_goals: int = Field(alias="skshg")
    sk_shot_attempts: int = Field(alias="skshotattempts")
    sk_shot_on_net_pct: float = Field(alias="skshotonnetpct")
    sk_shot_pct: float = Field(alias="skshotpct")
    sk_shots: int = Field(alias="skshots")
    sk_takeaways: int = Field(alias="sktakeaways")
    team_art_abbr: str = Field(alias="teamArtAbbr")
    team_id: int = Field(alias="teamId")
    team_side: int = Field(alias="teamSide")
    toi: int = Field(alias="toi")
    toi_seconds: int = Field(alias="toiseconds")