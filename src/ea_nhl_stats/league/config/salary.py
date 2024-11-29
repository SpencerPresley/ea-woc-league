"""Salary configuration and validation.

This module defines the configuration for salary caps, floors, and contract rules
in a league. It includes position-specific and manager-specific salary ranges.
"""

from typing import Dict, Optional, TypeVar, Type, ClassVar
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    NonNegativeInt
)

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import LeagueTier, ManagerRole


T = TypeVar('T', bound='SalaryRange')


class SalaryRange(BaseModel):
    """Defines minimum and maximum salary for a position or role.
    
    Attributes:
        minimum: Minimum allowed salary in this range
        maximum: Maximum allowed salary in this range
        is_prorated: Whether salaries in this range can be prorated
    """
    
    model_config = ConfigDict(frozen=True)
    
    minimum: NonNegativeInt = Field(
        description="Minimum allowed salary in this range"
    )
    maximum: NonNegativeInt = Field(
        description="Maximum allowed salary in this range"
    )
    is_prorated: bool = Field(
        default=False,
        description="Whether salaries in this range can be prorated"
    )
    
    @model_validator(mode='after')
    def validate_range(self) -> 'SalaryRange':
        """Validate that minimum <= maximum.
        
        Returns:
            self: The validated SalaryRange instance
            
        Raises:
            ValueError: If minimum > maximum
        """
        if self.minimum > self.maximum:
            raise ValueError(
                f"Minimum salary ({self.minimum}) cannot be greater than "
                f"maximum salary ({self.maximum})"
            )
        return self
    
    @classmethod
    def create(
        cls: Type[T],
        minimum: int,
        maximum: int,
        is_prorated: bool = False
    ) -> T:
        """Create a new SalaryRange instance.
        
        Args:
            minimum: Minimum allowed salary
            maximum: Maximum allowed salary
            is_prorated: Whether salaries can be prorated
            
        Returns:
            A new SalaryRange instance
            
        Raises:
            ValueError: If minimum > maximum or if any value is negative
        """
        return cls(
            minimum=minimum,
            maximum=maximum,
            is_prorated=is_prorated
        )


class SalaryRules(BaseModel):
    """Configuration for salary cap and contract rules.
    
    Attributes:
        tier: League tier these rules apply to
        salary_cap: Maximum total team salary allowed
        minimum_team_salary: Minimum total team salary required (floor)
        position_salary_ranges: Salary ranges for each position
        manager_salary_ranges: Salary ranges for each manager role
        max_contract_length: Maximum length of any contract in years
        max_contract_value: Maximum total value of any single contract
        allow_performance_bonuses: Whether performance bonuses are allowed
        minimum_contract_length: Minimum length of any contract in years
    """
    
    # League tier constants
    DEFAULT_NHL_CAP: ClassVar[int] = 82_500_000
    DEFAULT_AHL_CAP: ClassVar[int] = 50_000_000
    DEFAULT_ECHL_CAP: ClassVar[int] = 25_000_000
    DEFAULT_CHL_CAP: ClassVar[int] = 15_000_000
    
    # Contract length constants
    DEFAULT_MAX_CONTRACT_LENGTH: ClassVar[int] = 8
    DEFAULT_MIN_CONTRACT_LENGTH: ClassVar[int] = 1
    
    model_config = ConfigDict(frozen=True)
    
    # Basic configuration
    tier: LeagueTier = Field(description="League tier these rules apply to")
    salary_cap: NonNegativeInt = Field(description="Maximum total team salary allowed")
    minimum_team_salary: NonNegativeInt = Field(description="Minimum total team salary required")
    
    # Salary ranges
    position_salary_ranges: Dict[Position, SalaryRange] = Field(
        description="Salary ranges for each position"
    )
    manager_salary_ranges: Dict[ManagerRole, SalaryRange] = Field(
        description="Salary ranges for each manager role"
    )
    
    # Contract rules
    max_contract_length: NonNegativeInt = Field(
        default=DEFAULT_MAX_CONTRACT_LENGTH,
        description="Maximum length of any contract in years"
    )
    max_contract_value: NonNegativeInt = Field(
        description="Maximum total value of any single contract"
    )
    minimum_contract_length: NonNegativeInt = Field(
        default=DEFAULT_MIN_CONTRACT_LENGTH,
        description="Minimum length of any contract in years"
    )
    allow_performance_bonuses: bool = Field(
        default=False,
        description="Whether performance bonuses are allowed"
    )
    
    @model_validator(mode='after')
    def validate_salary_rules(self) -> 'SalaryRules':
        """Validate salary cap rules.
        
        Returns:
            self: The validated SalaryRules instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate team salary range
        if self.minimum_team_salary > self.salary_cap:
            raise ValueError(
                f"Minimum team salary ({self.minimum_team_salary}) cannot exceed "
                f"salary cap ({self.salary_cap})"
            )
        
        # Validate contract lengths
        if self.minimum_contract_length > self.max_contract_length:
            raise ValueError(
                f"Minimum contract length ({self.minimum_contract_length}) cannot exceed "
                f"maximum contract length ({self.max_contract_length})"
            )
        
        # Validate max contract value against cap
        if self.max_contract_value > self.salary_cap:
            raise ValueError(
                f"Maximum contract value ({self.max_contract_value}) cannot exceed "
                f"salary cap ({self.salary_cap})"
            )
        
        return self
    
    @classmethod
    def create_for_tier(
        cls,
        tier: LeagueTier,
        *,
        custom_cap: Optional[int] = None,
        custom_floor_percentage: Optional[float] = None,
        max_contract_years: Optional[int] = None
    ) -> 'SalaryRules':
        """Create salary rules appropriate for a league tier.
        
        Args:
            tier: The league tier to create rules for
            custom_cap: Optional custom salary cap value
            custom_floor_percentage: Optional custom salary floor percentage
            max_contract_years: Optional custom maximum contract length
            
        Returns:
            SalaryRules configured for the specified tier
        """
        # Determine base values for tier
        base_cap = custom_cap or {
            LeagueTier.NHL: cls.DEFAULT_NHL_CAP,
            LeagueTier.AHL: cls.DEFAULT_AHL_CAP,
            LeagueTier.ECHL: cls.DEFAULT_ECHL_CAP,
            LeagueTier.CHL: cls.DEFAULT_CHL_CAP
        }[tier]
        
        # Calculate floor (default 85% of cap for NHL, 75% for others)
        floor_percentage = custom_floor_percentage or (
            0.85 if tier == LeagueTier.NHL else 0.75
        )
        floor = int(base_cap * floor_percentage)
        
        # Determine contract length
        max_years = max_contract_years or (
            8 if tier == LeagueTier.NHL else
            6 if tier == LeagueTier.AHL else
            4 if tier == LeagueTier.ECHL else
            3  # CHL
        )
        
        # Create position salary ranges based on tier
        position_ranges = cls._create_position_ranges(tier, base_cap)
        
        # Create manager salary ranges based on tier
        manager_ranges = cls._create_manager_ranges(tier)
        
        return cls(
            tier=tier,
            salary_cap=base_cap,
            minimum_team_salary=floor,
            position_salary_ranges=position_ranges,
            manager_salary_ranges=manager_ranges,
            max_contract_length=max_years,
            max_contract_value=int(base_cap * 0.2),  # 20% of cap
            allow_performance_bonuses=tier in {LeagueTier.NHL, LeagueTier.AHL}
        )
    
    @staticmethod
    def _create_position_ranges(
        tier: LeagueTier,
        cap: int
    ) -> Dict[Position, SalaryRange]:
        """Create position-specific salary ranges for a tier.
        
        Args:
            tier: League tier to create ranges for
            cap: Salary cap for the tier
            
        Returns:
            Dictionary mapping positions to their salary ranges
        """
        # Base percentages of cap for each position
        if tier == LeagueTier.NHL:
            ranges = {
                Position.GOALIE: (0.05, 0.15),        # 5-15% of cap
                Position.CENTER: (0.05, 0.15),        # 5-15% of cap
                Position.LEFT_WING: (0.04, 0.12),     # 4-12% of cap
                Position.RIGHT_WING: (0.04, 0.12),    # 4-12% of cap
                Position.LEFT_DEFENSE: (0.04, 0.13),  # 4-13% of cap
                Position.RIGHT_DEFENSE: (0.04, 0.13), # 4-13% of cap
            }
        else:
            # Lower tiers have compressed salary ranges
            ranges = {
                Position.GOALIE: (0.04, 0.12),        # 4-12% of cap
                Position.CENTER: (0.04, 0.12),        # 4-12% of cap
                Position.LEFT_WING: (0.03, 0.10),     # 3-10% of cap
                Position.RIGHT_WING: (0.03, 0.10),    # 3-10% of cap
                Position.LEFT_DEFENSE: (0.03, 0.11),  # 3-11% of cap
                Position.RIGHT_DEFENSE: (0.03, 0.11), # 3-11% of cap
            }
        
        return {
            pos: SalaryRange(
                minimum=int(cap * min_pct),
                maximum=int(cap * max_pct),
                is_prorated=tier in {LeagueTier.NHL, LeagueTier.AHL}
            )
            for pos, (min_pct, max_pct) in ranges.items()
        }
    
    @staticmethod
    def _create_manager_ranges(tier: LeagueTier) -> Dict[ManagerRole, SalaryRange]:
        """Create manager-specific salary ranges for a tier.
        
        Args:
            tier: League tier to create ranges for
            
        Returns:
            Dictionary mapping manager roles to their salary ranges
        """
        if tier == LeagueTier.NHL:
            return {
                ManagerRole.OWNER: SalaryRange(minimum=0, maximum=0),
                ManagerRole.GM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.AGM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.PAID_AGM: SalaryRange(minimum=50_000, maximum=150_000)
            }
        elif tier == LeagueTier.AHL:
            return {
                ManagerRole.GM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.AGM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.PAID_AGM: SalaryRange(minimum=35_000, maximum=100_000)
            }
        elif tier == LeagueTier.ECHL:
            return {
                ManagerRole.OWNER: SalaryRange(minimum=0, maximum=0),
                ManagerRole.GM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.AGM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.PAID_AGM: SalaryRange(minimum=25_000, maximum=75_000)
            }
        else:  # CHL
            return {
                ManagerRole.OWNER: SalaryRange(minimum=0, maximum=0),
                ManagerRole.GM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.AGM: SalaryRange(minimum=0, maximum=0),
                ManagerRole.PAID_AGM: SalaryRange(minimum=20_000, maximum=50_000)
            } 