"""Enums for game-related models."""

from enum import Enum


class Position(Enum):
    """
    Enum representing player positions on the ice.
    
    Attributes:
        NULL (int): Represents no position or an invalid position.
        CENTER (int): Represents the Center position.
        LEFT_WING (int): Represents the Left Wing position.
        RIGHT_WING (int): Represents the Right Wing position.
        LEFT_DEFENSE (int): Represents the Left Defense position.
        RIGHT_DEFENSE (int): Represents the Right Defense position.
        GOALIE (int): Represents the Goalie position.
    """
    NULL = 0
    CENTER = 1
    LEFT_WING = 2
    RIGHT_WING = 3
    LEFT_DEFENSE = 4
    RIGHT_DEFENSE = 5
    GOALIE = 6


class TeamSide(Enum):
    """Team side enumeration."""
    HOME = 0
    AWAY = 1 