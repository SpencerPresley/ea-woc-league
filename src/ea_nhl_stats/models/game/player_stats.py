"""Player statistics models."""

from dataclasses import dataclass
from pydantic import BaseModel, Field
from ea_nhl_stats.models.game.enums import Position


@dataclass
class PlayerStatsForSingleGame:
    """Dataclass representing a player's stats for a single game.
    
    Attributes:
        position: The position the player played in the game
        playername: The name of the player
        blocked_shots: Number of shots blocked
        short_handed_goals: Number of short-handed goals scored
        puck_possession_seconds: Time in seconds player had puck possession
    """
    position: Position
    playername: str
    blocked_shots: int = 0
    short_handed_goals: int = 0
    puck_possession_seconds: int = 0


class PlayerStats(BaseModel):
    """Model representing player statistics from a game.
    
    Attributes:
        player_id: Unique identifier for the player
        position: Player's position in the game
        goals: Number of goals scored
        assists: Number of assists
        shots: Number of shots taken
        hits: Number of hits delivered
        puck_possession_seconds: Time in seconds player had puck possession
        penalty_minutes: Number of penalty minutes
        plus_minus: Plus/minus rating for the game
        blocked_shots: Number of shots blocked
        short_handed_goals: Number of short-handed goals scored
    """
    
    player_id: int = Field(..., description="Unique identifier for the player")
    position: Position = Field(..., description="Player's position in the game")
    goals: int = Field(0, ge=0, description="Number of goals scored")
    assists: int = Field(0, ge=0, description="Number of assists")
    shots: int = Field(0, ge=0, description="Number of shots taken")
    hits: int = Field(0, ge=0, description="Number of hits delivered")
    puck_possession_seconds: int = Field(0, ge=0, description="Time in seconds player had puck possession")
    penalty_minutes: int = Field(0, ge=0, description="Number of penalty minutes")
    plus_minus: int = Field(0, description="Plus/minus rating for the game")
    blocked_shots: int = Field(0, ge=0, description="Number of shots blocked")
    short_handed_goals: int = Field(0, ge=0, description="Number of short-handed goals scored") 