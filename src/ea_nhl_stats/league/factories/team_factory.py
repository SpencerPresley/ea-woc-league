"""Team factory for creating team instances.

This module provides the factory pattern implementation for creating team instances.
It manages the registration and instantiation of concrete team implementations.
"""

from typing import ClassVar, Dict, Type

from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam


class TeamFactory:
    """Factory for creating team instances.
    
    This class implements the factory pattern for teams, managing the registration
    and creation of concrete team implementations. It ensures type safety by using
    TeamIdentifier enum for registration and lookup.
    """
    
    _teams: ClassVar[Dict[TeamIdentifier, Type[LeagueTeam]]] = {}
    
    @classmethod
    def register(cls, identifier: TeamIdentifier):
        """Register a team implementation.
        
        Args:
            identifier: The team identifier to register
            
        Returns:
            Decorator function for the team class
        """
        def decorator(team_class: Type[LeagueTeam]):
            cls._teams[identifier] = team_class
            return team_class
        return decorator
    
    @classmethod
    def create(cls, identifier: TeamIdentifier, **kwargs) -> LeagueTeam:
        """Create a team instance by identifier.
        
        Args:
            identifier: The team identifier to create
            **kwargs: Additional arguments for team creation
            
        Returns:
            New team instance
            
        Raises:
            ValueError: If no implementation exists for the identifier
        """
        if identifier not in cls._teams:
            raise ValueError(f"No implementation for team: {identifier}")
        return cls._teams[identifier](**kwargs) 