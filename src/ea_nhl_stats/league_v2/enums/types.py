"""Core type enumerations for the league management system.

This module defines the fundamental enumeration types used throughout the league
management system. These enums provide type-safe options for various aspects of
the system, particularly focusing on management roles.

The key enums are:
    - ManagerRole: Defines the possible management positions within a team

Example:
    Checking if a role is a GM:
        >>> role = ManagerRole.GM
        >>> is_gm = role == ManagerRole.GM
"""

from enum import Enum, auto


class ManagerRole(Enum):
    """Management roles within a team.
    
    This enum defines the possible management positions that a player can hold
    within a team's organization.
    
    Attributes:
        OWNER: Team owner - typically has full control
        GM: General Manager - manages team operations
        AGM: Assistant General Manager - assists the GM
        PAID_AGM: Paid Assistant GM - compensated AGM position
        
    Note:
        The string values are used for database storage and API communication.
    """
    
    OWNER = "owner"     # Team owner
    GM = "gm"          # General Manager
    AGM = "agm"        # Assistant General Manager
    PAID_AGM = "paid_agm"  # Paid Assistant GM 


class Position(Enum):
    """Player positions."""
    CENTER = auto()
    LEFT_WING = auto()
    RIGHT_WING = auto()
    LEFT_DEFENSE = auto()
    RIGHT_DEFENSE = auto()
    GOALIE = auto()