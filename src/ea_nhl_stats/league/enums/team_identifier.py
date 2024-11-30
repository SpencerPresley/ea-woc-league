"""Team identifier enumeration.

This module provides the enum for identifying teams across the league system.
These identifiers are permanent and independent of EA NHL game identifiers.
"""

from enum import Enum


class TeamIdentifier(str, Enum):
    """Team identifiers and their official display names.
    
    These are the permanent identifiers for teams in the league system.
    The string values are the official display names used for presentation.
    
    Note:
        These identifiers are independent of EA NHL game identifiers,
        which can change between games and seasons.
    """
    
    # NHL Teams
    ST_LOUIS_BLUES = "St. Louis Blues"
    CALGARY_FLAMES = "Calgary Flames"
    # AHL Teams can be added here
    # SPRINGFIELD_THUNDERBIRDS = "Springfield Thunderbirds"
    # ECHL Teams can be added here 