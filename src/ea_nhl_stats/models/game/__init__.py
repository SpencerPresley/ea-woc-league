"""Game-related models package."""

from ea_nhl_stats.league.enums.types import Position
from enum import Enum

class TeamSide(str, Enum):
    """Enum for team sides in a match."""
    HOME = "home"
    AWAY = "away"

from .ea_player_stats import PlayerStats
from .ea_club_stats import ClubStats
from .ea_match import Match

__all__ = [
    'Position',
    'TeamSide',
    'PlayerStats',
    'ClubStats',
    'Match'
] 