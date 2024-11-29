"""Game result models."""

from datetime import datetime
import shortuuid
from urllib.parse import quote
from pydantic import BaseModel, Field, field_validator
from typing import Any

from ea_nhl_stats.models.game.enums import TeamSide
from ea_nhl_stats.models.game.team_stats import TeamStats


class GameResult(BaseModel):
    """Model representing the result of a game.
    
    Attributes:
        game_id: Unique identifier for the game
        timestamp: ISO format timestamp of when the game was played
        winner: Which team won (home or away)
        score: Score in format "home-away" (e.g. "3-2")
        home_team: Stats for the home team
        away_team: Stats for the away team
        time_created: When this record was created
        game_url_suffix: URL-safe unique identifier for the game
    """
    
    game_id: int = Field(..., description="Unique identifier for the game")
    timestamp: str = Field(..., description="ISO format timestamp of when the game was played")
    winner: TeamSide = Field(..., description="Which team won (home or away)")
    score: str = Field(..., description="Score in format 'home-away' (e.g. '3-2')")
    home_team: TeamStats = Field(..., description="Stats for the home team")
    away_team: TeamStats = Field(..., description="Stats for the away team")
    time_created: datetime = Field(default_factory=datetime.now, description="When this record was created")
    game_url_suffix: str = Field(default="", description="URL-safe unique identifier for the game")
    
    @field_validator('score')
    @classmethod
    def validate_score_format(cls, v: str) -> str:
        """Validate score is in correct format.
        
        Args:
            v: Score string to validate
            
        Returns:
            The validated score string
            
        Raises:
            ValueError: If score format is invalid
        """
        if not v or '-' not in v:
            raise ValueError('Score must be in format "home-away" (e.g. "3-2")')
        
        home_score, away_score = v.split('-')
        try:
            int(home_score)
            int(away_score)
        except ValueError as e:
            raise ValueError('Score values must be integers') from e
            
        return v
        
    def model_post_init(self, __context: Any) -> None:
        """Post initialization processing.
        
        Sets the game URL suffix if not already set.
        """
        if not self.game_url_suffix:
            game_identifier = f"{self.home_team.club_id}-{self.away_team.club_id}-{self.time_created.timestamp()}"
            self.game_url_suffix = quote(str(shortuuid.uuid(name=game_identifier))) 