"""Tests for league type enumerations."""

from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.league.enums.types import ManagerRole, Position

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


def test_manager_role_values():
    """Test manager role enum values."""
    assert ManagerRole.OWNER.value == "owner"
    assert ManagerRole.GM.value == "gm"
    assert ManagerRole.AGM.value == "agm"
    assert ManagerRole.PAID_AGM.value == "paid_agm"


def test_manager_role_comparison():
    """Test manager role comparison."""
    role = ManagerRole.GM
    assert role == ManagerRole.GM
    assert role != ManagerRole.OWNER
    assert role in ManagerRole


def test_position_values():
    """Test position enum values."""
    # Test all positions exist
    assert Position.CENTER
    assert Position.LEFT_WING
    assert Position.RIGHT_WING
    assert Position.LEFT_DEFENSE
    assert Position.RIGHT_DEFENSE
    assert Position.GOALIE


def test_position_comparison():
    """Test position comparison."""
    pos = Position.CENTER
    assert pos == Position.CENTER
    assert pos != Position.LEFT_WING
    assert pos in Position


def test_position_uniqueness():
    """Test that all position values are unique."""
    values = [pos.value for pos in Position]
    assert len(values) == len(set(values))  # No duplicates 