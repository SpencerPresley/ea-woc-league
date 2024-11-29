"""Tests for salary configuration."""

from typing import TYPE_CHECKING, Dict

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import LeagueTier, ManagerRole
from ea_nhl_stats.league.config.salary import SalaryRange, SalaryRules

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


class TestSalaryRange:
    """Test cases for SalaryRange configuration."""
    
    def test_valid_range(self) -> None:
        """Test creation with valid salary range."""
        range_ = SalaryRange(minimum=50_000, maximum=100_000)
        assert range_.minimum == 50_000
        assert range_.maximum == 100_000
        assert not range_.is_prorated
    
    def test_equal_range(self) -> None:
        """Test creation with equal min and max."""
        range_ = SalaryRange(minimum=75_000, maximum=75_000)
        assert range_.minimum == range_.maximum
    
    def test_invalid_range(self) -> None:
        """Test that invalid ranges raise ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            SalaryRange(minimum=100_000, maximum=50_000)
        assert "cannot be greater than" in str(exc_info.value)
    
    def test_negative_salary(self) -> None:
        """Test that negative salaries raise ValidationError."""
        with pytest.raises(ValidationError):
            SalaryRange(minimum=-50_000, maximum=100_000)
        
        with pytest.raises(ValidationError):
            SalaryRange(minimum=50_000, maximum=-100_000)
    
    def test_create_method(self) -> None:
        """Test the create class method."""
        range_ = SalaryRange.create(
            minimum=50_000,
            maximum=100_000,
            is_prorated=True
        )
        assert range_.minimum == 50_000
        assert range_.maximum == 100_000
        assert range_.is_prorated


class TestSalaryRules:
    """Test cases for SalaryRules configuration."""
    
    def test_nhl_defaults(self) -> None:
        """Test default values for NHL tier."""
        rules = SalaryRules.create_for_tier(LeagueTier.NHL)
        
        # Check basic values
        assert rules.tier == LeagueTier.NHL
        assert rules.salary_cap == SalaryRules.DEFAULT_NHL_CAP
        assert rules.minimum_team_salary == int(SalaryRules.DEFAULT_NHL_CAP * 0.85)
        assert rules.max_contract_length == 8
        assert rules.allow_performance_bonuses is True
        
        # Check position ranges
        assert Position.CENTER in rules.position_salary_ranges
        center_range = rules.position_salary_ranges[Position.CENTER]
        assert center_range.minimum == int(SalaryRules.DEFAULT_NHL_CAP * 0.05)
        assert center_range.maximum == int(SalaryRules.DEFAULT_NHL_CAP * 0.15)
        assert center_range.is_prorated is True
        
        # Check manager ranges
        assert ManagerRole.PAID_AGM in rules.manager_salary_ranges
        paid_agm_range = rules.manager_salary_ranges[ManagerRole.PAID_AGM]
        assert paid_agm_range.minimum == 50_000
        assert paid_agm_range.maximum == 150_000
    
    def test_ahl_defaults(self) -> None:
        """Test default values for AHL tier."""
        rules = SalaryRules.create_for_tier(LeagueTier.AHL)
        
        assert rules.tier == LeagueTier.AHL
        assert rules.salary_cap == SalaryRules.DEFAULT_AHL_CAP
        assert rules.minimum_team_salary == int(SalaryRules.DEFAULT_AHL_CAP * 0.75)
        assert rules.max_contract_length == 6
        assert rules.allow_performance_bonuses is True
    
    def test_custom_cap(self) -> None:
        """Test creation with custom salary cap."""
        custom_cap = 100_000_000
        rules = SalaryRules.create_for_tier(
            LeagueTier.NHL,
            custom_cap=custom_cap
        )
        
        assert rules.salary_cap == custom_cap
        assert rules.minimum_team_salary == int(custom_cap * 0.85)
        
        # Check that position ranges scale with custom cap
        center_range = rules.position_salary_ranges[Position.CENTER]
        assert center_range.minimum == int(custom_cap * 0.05)
        assert center_range.maximum == int(custom_cap * 0.15)
    
    def test_custom_floor_percentage(self) -> None:
        """Test creation with custom salary floor percentage."""
        rules = SalaryRules.create_for_tier(
            LeagueTier.NHL,
            custom_floor_percentage=0.90
        )
        
        assert rules.minimum_team_salary == int(SalaryRules.DEFAULT_NHL_CAP * 0.90)
    
    def test_custom_contract_length(self) -> None:
        """Test creation with custom maximum contract length."""
        rules = SalaryRules.create_for_tier(
            LeagueTier.NHL,
            max_contract_years=5
        )
        
        assert rules.max_contract_length == 5
    
    def test_invalid_floor(self) -> None:
        """Test that invalid salary floor raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            SalaryRules(
                tier=LeagueTier.NHL,
                salary_cap=1_000_000,
                minimum_team_salary=2_000_000,  # Floor > Cap
                position_salary_ranges={},
                manager_salary_ranges={},
                max_contract_value=200_000
            )
        assert "cannot exceed salary cap" in str(exc_info.value)
    
    def test_invalid_contract_length(self) -> None:
        """Test that invalid contract length raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            SalaryRules(
                tier=LeagueTier.NHL,
                salary_cap=1_000_000,
                minimum_team_salary=800_000,
                position_salary_ranges={},
                manager_salary_ranges={},
                max_contract_value=200_000,
                minimum_contract_length=5,
                max_contract_length=3  # Min > Max
            )
        assert "cannot exceed maximum contract length" in str(exc_info.value)
    
    def test_invalid_contract_value(self) -> None:
        """Test that invalid max contract value raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            SalaryRules(
                tier=LeagueTier.NHL,
                salary_cap=1_000_000,
                minimum_team_salary=800_000,
                position_salary_ranges={},
                manager_salary_ranges={},
                max_contract_value=1_200_000  # > Cap
            )
        assert "cannot exceed salary cap" in str(exc_info.value)
    
    @pytest.mark.parametrize("tier", list(LeagueTier))
    def test_position_ranges_sum(self, tier: LeagueTier) -> None:
        """Test that position salary ranges are reasonable.
        
        The sum of maximum salaries for a standard lineup should not
        exceed the salary cap.
        """
        rules = SalaryRules.create_for_tier(tier)
        
        # Standard lineup maximums
        lineup_max = sum([
            rules.position_salary_ranges[Position.CENTER].maximum,      # 1C
            rules.position_salary_ranges[Position.LEFT_WING].maximum,   # 1LW
            rules.position_salary_ranges[Position.RIGHT_WING].maximum,  # 1RW
            rules.position_salary_ranges[Position.LEFT_DEFENSE].maximum,  # 1LD
            rules.position_salary_ranges[Position.RIGHT_DEFENSE].maximum, # 1RD
            rules.position_salary_ranges[Position.GOALIE].maximum       # 1G
        ])
        
        assert lineup_max <= rules.salary_cap 