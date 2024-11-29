"""League configuration package.

This package contains configuration classes for various aspects of league management,
including roster limits, salary rules, and manager rules.
"""

from .roster import PositionLimit, RosterLimits
from .salary import SalaryRange, SalaryRules

__all__ = [
    'PositionLimit',
    'RosterLimits',
    'SalaryRange',
    'SalaryRules',
] 