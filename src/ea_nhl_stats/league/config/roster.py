"""Roster configuration and validation.

This module defines the configuration for roster limits and position distributions
in a league.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

from pydantic import BaseModel, Field, model_validator

from ea_nhl_stats.models.game.enums import Position


class PositionLimit(BaseModel):
    """Limits for a specific position.
    
    Attributes:
        min_count: Minimum number of players required for this position
        max_count: Maximum number of players allowed for this position
    """
    
    min_count: int = Field(ge=0, description="Minimum number of players required")
    max_count: int = Field(ge=0, description="Maximum number of players allowed")
    
    @model_validator(mode='after')
    def validate_limits(self) -> 'PositionLimit':
        """Validate that min_count <= max_count.
        
        Returns:
            self: The validated PositionLimit instance
            
        Raises:
            ValueError: If min_count > max_count
        """
        if self.min_count > self.max_count:
            raise ValueError(
                f"Minimum count ({self.min_count}) cannot be greater than "
                f"maximum count ({self.max_count})"
            )
        return self


class RosterLimits(BaseModel):
    """Configuration for roster size and position limits.
    
    Attributes:
        max_players: Maximum total players allowed on roster
        max_forwards: Maximum forwards allowed on roster
        max_defense: Maximum defensemen allowed on roster
        max_goalies: Maximum goalies allowed on roster
        position_limits: Specific limits for each position
    """
    
    max_players: int = Field(
        default=17,
        ge=1,
        description="Maximum total players allowed on roster"
    )
    max_forwards: int = Field(
        default=9,
        ge=0,
        description="Maximum forwards allowed on roster"
    )
    max_defense: int = Field(
        default=6,
        ge=0,
        description="Maximum defensemen allowed on roster"
    )
    max_goalies: int = Field(
        default=2,
        ge=0,
        description="Maximum goalies allowed on roster"
    )
    position_limits: Dict[Position, PositionLimit] = Field(
        default_factory=dict,
        description="Specific limits for each position"
    )
    
    @model_validator(mode='after')
    def validate_totals(self) -> 'RosterLimits':
        """Validate that position maximums sum correctly.
        
        Returns:
            self: The validated RosterLimits instance
            
        Raises:
            ValueError: If position maximums don't sum correctly
        """
        # Validate that max positions sum to max_players
        total_max = (
            self.max_forwards +
            self.max_defense +
            self.max_goalies
        )
        
        if total_max != self.max_players:
            raise ValueError(
                f"Sum of maximum positions ({total_max}) must equal "
                f"maximum players ({self.max_players})"
            )
        
        # If position limits are specified, validate their sums
        if self.position_limits:
            forward_positions = [
                Position.LEFT_WING,
                Position.CENTER,
                Position.RIGHT_WING
            ]
            defense_positions = [
                Position.LEFT_DEFENSE,
                Position.RIGHT_DEFENSE
            ]
            goalie_positions = [Position.GOALIE]
            
            # Check forward positions
            forward_max = sum(
                self.position_limits[pos].max_count
                for pos in forward_positions
                if pos in self.position_limits
            )
            if forward_max > self.max_forwards:
                raise ValueError(
                    f"Sum of forward position maximums ({forward_max}) cannot exceed "
                    f"maximum forwards ({self.max_forwards})"
                )
            
            # Check defense positions
            defense_max = sum(
                self.position_limits[pos].max_count
                for pos in defense_positions
                if pos in self.position_limits
            )
            if defense_max > self.max_defense:
                raise ValueError(
                    f"Sum of defense position maximums ({defense_max}) cannot exceed "
                    f"maximum defense ({self.max_defense})"
                )
            
            # Check goalie positions
            goalie_max = sum(
                self.position_limits[pos].max_count
                for pos in goalie_positions
                if pos in self.position_limits
            )
            if goalie_max > self.max_goalies:
                raise ValueError(
                    f"Sum of goalie position maximums ({goalie_max}) cannot exceed "
                    f"maximum goalies ({self.max_goalies})"
                )
        
        return self
    
    @classmethod
    def create_default(cls) -> 'RosterLimits':
        """Create a RosterLimits instance with default NHL-style limits.
        
        Returns:
            RosterLimits: A new instance with default NHL-style limits
        """
        return cls(
            max_players=17,
            max_forwards=9,
            max_defense=6,
            max_goalies=2,
            position_limits={
                Position.LEFT_WING: PositionLimit(min_count=2, max_count=3),
                Position.CENTER: PositionLimit(min_count=2, max_count=3),
                Position.RIGHT_WING: PositionLimit(min_count=2, max_count=3),
                Position.LEFT_DEFENSE: PositionLimit(min_count=2, max_count=3),
                Position.RIGHT_DEFENSE: PositionLimit(min_count=2, max_count=3),
                Position.GOALIE: PositionLimit(min_count=2, max_count=2)
            }
        ) 