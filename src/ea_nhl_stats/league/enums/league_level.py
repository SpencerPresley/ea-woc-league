"""League level enumeration.

This module provides the enum for different levels in the hockey league system.
"""

from enum import Enum


class LeagueLevel(str, Enum):
    """Hockey league levels.
    
    These represent the different tiers in the hockey league system,
    from the top level (NHL) down through the minor leagues.
    """
    
    NHL = "nhl"   # National Hockey League
    AHL = "ahl"   # American Hockey League
    ECHL = "echl" # East Coast Hockey League 