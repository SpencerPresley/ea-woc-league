"""Team implementations.

This module contains concrete implementations of teams.
Each team is registered with the TeamFactory for league-wide management.
"""

from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.factories.team_factory import TeamFactory

@TeamFactory.register(TeamIdentifier.ST_LOUIS_BLUES)
class StLouisBlues(LeagueTeam):
    """St. Louis Blues NHL team implementation."""
    
    def __init__(self, **data):
        super().__init__(
            official_name=TeamIdentifier.ST_LOUIS_BLUES.value,
            league_level=LeagueLevel.NHL,
            **data
        )


@TeamFactory.register(TeamIdentifier.CALGARY_FLAMES)
class CalgaryFlames(LeagueTeam):
    """Calgary Flames NHL team implementation."""
    
    def __init__(self, **data):
        super().__init__(
            official_name=TeamIdentifier.CALGARY_FLAMES.value,
            league_level=LeagueLevel.NHL,
            **data
        ) 