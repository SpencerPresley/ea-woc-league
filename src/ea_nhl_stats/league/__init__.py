"""League management package.

This package contains all the code for managing leagues, teams, and players
in the EA NHL league system.
"""

from .enums import LeagueTier, ManagerRole, LeagueStateType

__all__ = [
    'LeagueTier',
    'ManagerRole',
    'LeagueStateType',
] 