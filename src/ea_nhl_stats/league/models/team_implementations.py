"""Team implementations.

This module contains concrete implementations of teams.
Each team is registered with the TeamRegistry for league-wide management.
"""

from enum import Enum

from ea_nhl_stats.league.models.team import LeagueTeam, TeamRegistry, LeagueLevel


class TeamIdentifier(str, Enum):
    """Team identifiers and their official display names."""
    # NHL Teams
    ST_LOUIS_BLUES = "St. Louis Blues"
    CALGARY_FLAMES = "Calgary Flames"
    # AHL Teams can be added here
    # SPRINGFIELD_THUNDERBIRDS = "Springfield Thunderbirds"
    # ECHL Teams can be added here


@TeamRegistry.register(TeamIdentifier.ST_LOUIS_BLUES)
class StLouisBlues(LeagueTeam):
    """St. Louis Blues NHL team implementation."""
    
    def __init__(self, **data):
        super().__init__(
            official_name=TeamIdentifier.ST_LOUIS_BLUES.value,
            league_level=LeagueLevel.NHL,
            **data
        )


@TeamRegistry.register(TeamIdentifier.CALGARY_FLAMES)
class CalgaryFlames(LeagueTeam):
    """Calgary Flames NHL team implementation."""
    
    def __init__(self, **data):
        super().__init__(
            official_name=TeamIdentifier.CALGARY_FLAMES.value,
            league_level=LeagueLevel.NHL,
            **data
        ) 