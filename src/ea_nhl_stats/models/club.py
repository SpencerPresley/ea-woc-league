"""
Models for club information and related data structures.

This module provides data models for representing club information, including
team details, statistics, and historical performance data. All models use
Pydantic for validation and data transformation.
"""

from typing import Dict, Optional
import re

from pydantic import (
    BaseModel,
    Field,
    RootModel,
    ValidationError,
    field_validator,
    model_validator,
)


class CustomKit(BaseModel):
    """
    Represents custom team kit (uniform) configuration.

    Attributes:
        is_custom_team: Flag indicating if team uses custom uniforms (0 or 1)
        crest_asset_id: Identifier for the team's crest asset
        use_base_asset: Flag indicating if base assets are used (0 or 1)
    """
    
    is_custom_team: int = Field(alias="isCustomTeam")
    crest_asset_id: str = Field(alias="crestAssetId")
    use_base_asset: int = Field(alias="useBaseAsset")

    @field_validator("is_custom_team", "use_base_asset", mode="before")
    @classmethod
    def convert_to_int(cls, v: str) -> int:
        """Convert string values to integers."""
        return int(v)


class ClubInfo(BaseModel):
    """
    Basic club information and identification.

    Attributes:
        name: Club name
        club_id: Unique identifier for the club
        region_id: Identifier for the club's region
        team_id: Identifier for the team
        custom_kit: Custom kit configuration
    """
    
    name: str
    club_id: int = Field(alias="clubId")
    region_id: int = Field(alias="regionId")
    team_id: int = Field(alias="teamId")
    custom_kit: CustomKit = Field(alias="customKit")

    @field_validator("club_id", "region_id", "team_id", mode="before")
    @classmethod
    def convert_to_int(cls, v: str) -> int:
        """Convert string values to integers."""
        return int(v)


class ClubData(BaseModel):
    """
    Comprehensive club data including statistics and historical performance.

    Contains detailed information about a club's performance, including:
    - Basic information (name, ID, etc.)
    - Competition results (wins, losses, etc.)
    - Historical performance (divisions won, cups won, etc.)
    - Recent match results
    - Season statistics
    """
    
    # Basic Information
    club_id: int = Field(alias="clubId", description="Unique club identifier")
    name: str = Field(description="Club name")
    rank: int = Field(description="Current rank")
    clubname: str = Field(description="Display name of the club")
    platform: str = Field(description="Gaming platform")
    
    # Competition History
    seasons: int = Field(description="Number of seasons played")
    div_groups_won: int = Field(alias="divGroupsWon", description="Total division groups won")
    leagues_won: int = Field(alias="leaguesWon", description="Total leagues won")
    
    # Division Group Wins by Level
    div_groups_won1: int = Field(alias="divGroupsWon1", description="Division 1 groups won")
    div_groups_won2: int = Field(alias="divGroupsWon2", description="Division 2 groups won")
    div_groups_won3: int = Field(alias="divGroupsWon3", description="Division 3 groups won")
    div_groups_won4: int = Field(alias="divGroupsWon4", description="Division 4 groups won")
    
    # Cup Performance
    cups_won1: int = Field(alias="cupsWon1", description="Type 1 cups won")
    cups_won2: int = Field(alias="cupsWon2", description="Type 2 cups won")
    cups_won3: int = Field(alias="cupsWon3", description="Type 3 cups won")
    cups_won4: int = Field(alias="cupsWon4", description="Type 4 cups won")
    cups_won5: int = Field(alias="cupsWon5", description="Type 5 cups won")
    
    # Cup Eliminations
    cups_elim1: int = Field(alias="cupsElim1", description="Type 1 cup eliminations")
    cups_elim2: int = Field(alias="cupsElim2", description="Type 2 cup eliminations")
    cups_elim3: int = Field(alias="cupsElim3", description="Type 3 cup eliminations")
    cups_elim4: int = Field(alias="cupsElim4", description="Type 4 cup eliminations")
    cups_elim5: int = Field(alias="cupsElim5", description="Type 5 cup eliminations")
    
    # Season Performance
    promotions: int = Field(description="Total promotions")
    holds: int = Field(description="Total holds")
    relegations: int = Field(description="Total relegations")
    ranking_points: int = Field(alias="rankingPoints", description="Current ranking points")
    
    # Division Information
    cur_competition: int = Field(alias="curCompetition", description="Current competition ID")
    prev_division: int = Field(alias="prevDivision", description="Previous division")
    prev_game_division: int = Field(alias="prevGameDivision", description="Previous game division")
    best_division: int = Field(alias="bestDivision", description="Best division achieved")
    best_points: int = Field(alias="bestPoints", description="Best points achieved")
    cur_season_mov: int = Field(alias="curSeasonMov", description="Current season movement")
    
    # Recent Match Results (0-9)
    recent_result0: int = Field(alias="recentResult0")
    recent_opponent0: int = Field(alias="recentOpponent0")
    recent_score0: str = Field(alias="recentScore0")
    recent_result1: int = Field(alias="recentResult1")
    recent_opponent1: int = Field(alias="recentOpponent1")
    recent_score1: str = Field(alias="recentScore1")
    recent_result2: int = Field(alias="recentResult2")
    recent_opponent2: int = Field(alias="recentOpponent2")
    recent_score2: str = Field(alias="recentScore2")
    recent_result3: int = Field(alias="recentResult3")
    recent_opponent3: int = Field(alias="recentOpponent3")
    recent_score3: str = Field(alias="recentScore3")
    recent_result4: int = Field(alias="recentResult4")
    recent_opponent4: int = Field(alias="recentOpponent4")
    recent_score4: str = Field(alias="recentScore4")
    recent_result5: int = Field(alias="recentResult5")
    recent_opponent5: int = Field(alias="recentOpponent5")
    recent_score5: str = Field(alias="recentScore5")
    recent_result6: int = Field(alias="recentResult6")
    recent_opponent6: int = Field(alias="recentOpponent6")
    recent_score6: str = Field(alias="recentScore6")
    recent_result7: int = Field(alias="recentResult7")
    recent_opponent7: int = Field(alias="recentOpponent7")
    recent_score7: str = Field(alias="recentScore7")
    recent_result8: int = Field(alias="recentResult8")
    recent_opponent8: int = Field(alias="recentOpponent8")
    recent_score8: str = Field(alias="recentScore8")
    recent_result9: int = Field(alias="recentResult9")
    recent_opponent9: int = Field(alias="recentOpponent9")
    recent_score9: str = Field(alias="recentScore9")
    
    # Season Statistics
    wins: int = Field(description="Total wins")
    losses: int = Field(description="Total losses")
    ties: int = Field(description="Total ties")
    otl: int = Field(description="Overtime losses")
    goals: int = Field(description="Goals scored")
    goals_against: int = Field(alias="goalsAgainst", description="Goals conceded")
    
    # Previous Season Statistics
    prev_season_wins: int = Field(alias="prevSeasonWins", description="Previous season wins")
    prev_season_losses: int = Field(alias="prevSeasonLosses", description="Previous season losses")
    prev_season_ties: int = Field(alias="prevSeasonTies", description="Previous season ties")
    prev_season_otl: int = Field(alias="prevSeasonOtl", description="Previous season overtime losses")
    
    # Additional Statistics
    star_level: int = Field(alias="starLevel", description="Star rating level")
    total_cups_won: int = Field(alias="totalCupsWon", description="Total cups won")
    cups_entered: int = Field(alias="cupsEntered", description="Total cups entered")
    cup_win_percent: int = Field(alias="cupWinPercent", description="Cup win percentage")
    titles_won: int = Field(alias="titlesWon", description="Total titles won")
    prev_game_won_title: int = Field(alias="prevGameWonTitle", description="Previous game title win flag")
    record: str = Field(description="Win-Loss-Tie record")
    clubfinalsplayed: int = Field(description="Total finals played")
    
    # Division Wins
    divs_won1: int = Field(alias="divsWon1", description="Division 1 wins")
    divs_won2: int = Field(alias="divsWon2", description="Division 2 wins")
    divs_won3: int = Field(alias="divsWon3", description="Division 3 wins")
    divs_won4: int = Field(alias="divsWon4", description="Division 4 wins")
    
    # Current Status
    current_division: int = Field(alias="currentDivision", description="Current division")
    club_info: ClubInfo = Field(alias="clubInfo", description="Detailed club information")

    @model_validator(mode="before")
    @classmethod
    def convert_ints(cls, data: Dict) -> Dict:
        """
        Convert string values to integers except for specific fields.
        
        Args:
            data: Dictionary of club data
            
        Returns:
            Dictionary with converted integer values
            
        Raises:
            ValueError: If value cannot be converted to integer
        """
        string_fields = {
            "name",
            "clubname",
            "record",
            "platform",
            "crestAssetId",
        }
        score_fields = {f"recentScore{i}" for i in range(10)}

        for field_name, value in data.items():
            if (
                isinstance(value, str)
                and field_name not in string_fields
                and field_name not in score_fields
            ):
                try:
                    data[field_name] = int(value)
                except ValueError:
                    raise ValueError(f"Invalid integer value for field '{field_name}'")
        return data

    @field_validator(
        "recent_score0",
        "recent_score1",
        "recent_score2",
        "recent_score3",
        "recent_score4",
        "recent_score5",
        "recent_score6",
        "recent_score7",
        "recent_score8",
        "recent_score9",
    )
    @classmethod
    def validate_score(cls, v: str) -> str:
        """
        Validate score format (must be 'int-int').
        
        Args:
            v: Score string to validate
            
        Returns:
            Validated score string
            
        Raises:
            ValueError: If score format is invalid
        """
        if not re.match(r"\d+-\d+", v):
            raise ValueError("Score must be in the format 'int-int'")
        return v


class ClubResponse(RootModel):
    """Root model containing a dictionary of club data indexed by club ID."""
    
    root: Dict[str, ClubData] 