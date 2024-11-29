"""League type enumerations.

This module contains enumerations for various league-related types including
league tiers, manager roles, and league states.
"""

from enum import Enum, auto
from typing import Dict, List


class LeagueTier(Enum):
    """Enumeration of league tiers in order of prestige.
    
    Attributes:
        NHL: National Hockey League - Tier 1
        AHL: American Hockey League - Tier 2
        ECHL: East Coast Hockey League - Tier 3
        CHL: Canadian Hockey League - Tier 4
    """
    
    NHL = 1
    AHL = 2
    ECHL = 3
    CHL = 4
    
    @property
    def display_name(self) -> str:
        """Get the display name of the league tier.
        
        Returns:
            str: Full name of the league tier.
        """
        return {
            LeagueTier.NHL: "National Hockey League",
            LeagueTier.AHL: "American Hockey League",
            LeagueTier.ECHL: "East Coast Hockey League",
            LeagueTier.CHL: "Canadian Hockey League"
        }[self]


class ManagerRole(Enum):
    """Enumeration of possible management roles within a team.
    
    Attributes:
        OWNER: Team owner - no contract value
        GM: General Manager - contract value varies by tier
        AGM: Assistant General Manager - contract value varies by tier
        PAID_AGM: Paid Assistant General Manager - always has positive contract value
    """
    
    OWNER = "owner"
    GM = "gm"
    AGM = "agm"
    PAID_AGM = "paid_agm"
    
    @property
    def can_have_salary(self) -> bool:
        """Check if the role can have a salary.
        
        Returns:
            bool: True if the role can have a salary, False otherwise.
        """
        return self in [ManagerRole.PAID_AGM]
    
    @property
    def display_name(self) -> str:
        """Get the display name of the role.
        
        Returns:
            str: Human-readable name of the role.
        """
        return {
            ManagerRole.OWNER: "Owner",
            ManagerRole.GM: "General Manager",
            ManagerRole.AGM: "Assistant General Manager",
            ManagerRole.PAID_AGM: "Paid Assistant General Manager"
        }[self]


class LeagueStateType(Enum):
    """Enumeration of possible league states.
    
    Attributes:
        SETUP: Initial league setup phase
        ACTIVE: Regular season active
        TRADING: Trade window open
        PLAYOFFS: Playoff period
        OFFSEASON: Off-season period
    """
    
    SETUP = auto()
    ACTIVE = auto()
    TRADING = auto()
    PLAYOFFS = auto()
    OFFSEASON = auto()
    
    @property
    def allows_trades(self) -> bool:
        """Check if trades are allowed in this state.
        
        Returns:
            bool: True if trades are allowed, False otherwise.
        """
        return self in [LeagueStateType.TRADING, LeagueStateType.OFFSEASON]
    
    @property
    def allows_signings(self) -> bool:
        """Check if player signings are allowed in this state.
        
        Returns:
            bool: True if signings are allowed, False otherwise.
        """
        return self in [LeagueStateType.SETUP, LeagueStateType.OFFSEASON]
    
    @property
    def display_name(self) -> str:
        """Get the display name of the state.
        
        Returns:
            str: Human-readable name of the state.
        """
        return self.name.title().replace('_', ' ') 