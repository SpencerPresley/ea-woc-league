"""Tests for league type enumerations."""

from typing import TYPE_CHECKING
import pytest

from ea_nhl_stats.league.enums.league_types import (
    LeagueTier,
    ManagerRole,
    LeagueStateType
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


class TestLeagueTier:
    """Test cases for LeagueTier enum."""
    
    def test_display_names(self) -> None:
        """Test that display names are correct for each tier."""
        assert LeagueTier.NHL.display_name == "National Hockey League"
        assert LeagueTier.AHL.display_name == "American Hockey League"
        assert LeagueTier.ECHL.display_name == "East Coast Hockey League"
        assert LeagueTier.CHL.display_name == "Canadian Hockey League"
    
    def test_values(self) -> None:
        """Test that enum values are correct and ordered."""
        assert LeagueTier.NHL.value == 1
        assert LeagueTier.AHL.value == 2
        assert LeagueTier.ECHL.value == 3
        assert LeagueTier.CHL.value == 4


class TestManagerRole:
    """Test cases for ManagerRole enum."""
    
    def test_display_names(self) -> None:
        """Test that display names are correct for each role."""
        assert ManagerRole.OWNER.display_name == "Owner"
        assert ManagerRole.GM.display_name == "General Manager"
        assert ManagerRole.AGM.display_name == "Assistant General Manager"
        assert ManagerRole.PAID_AGM.display_name == "Paid Assistant General Manager"
    
    def test_salary_permissions(self) -> None:
        """Test which roles can have salaries."""
        assert not ManagerRole.OWNER.can_have_salary
        assert not ManagerRole.GM.can_have_salary
        assert not ManagerRole.AGM.can_have_salary
        assert ManagerRole.PAID_AGM.can_have_salary


class TestLeagueStateType:
    """Test cases for LeagueStateType enum."""
    
    def test_display_names(self) -> None:
        """Test that display names are formatted correctly."""
        assert LeagueStateType.SETUP.display_name == "Setup"
        assert LeagueStateType.ACTIVE.display_name == "Active"
        assert LeagueStateType.TRADING.display_name == "Trading"
        assert LeagueStateType.PLAYOFFS.display_name == "Playoffs"
        assert LeagueStateType.OFFSEASON.display_name == "Offseason"
    
    def test_trade_permissions(self) -> None:
        """Test which states allow trades."""
        assert not LeagueStateType.SETUP.allows_trades
        assert not LeagueStateType.ACTIVE.allows_trades
        assert LeagueStateType.TRADING.allows_trades
        assert not LeagueStateType.PLAYOFFS.allows_trades
        assert LeagueStateType.OFFSEASON.allows_trades
    
    def test_signing_permissions(self) -> None:
        """Test which states allow player signings."""
        assert LeagueStateType.SETUP.allows_signings
        assert not LeagueStateType.ACTIVE.allows_signings
        assert not LeagueStateType.TRADING.allows_signings
        assert not LeagueStateType.PLAYOFFS.allows_signings
        assert LeagueStateType.OFFSEASON.allows_signings 