"""League management system.

This package provides the core functionality for managing the EA NHL league system,
including teams, players, statistics, and season management.
"""

from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.factories.team_factory import TeamFactory
from ea_nhl_stats.league.models.stats.player_stats import PlayerStats
from ea_nhl_stats.league.models.stats.team_stats import TeamStats
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam

__all__ = [
    'LeagueLevel',
    'TeamIdentifier',
    'TeamFactory',
    'PlayerStats',
    'TeamStats',
    'LeagueTeam',
] 