"""Tests for league level enumeration."""

from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.league.enums.league_level import LeagueLevel

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


def test_league_level_values():
    """Test league level enum values."""
    assert LeagueLevel.NHL.value == "nhl"
    assert LeagueLevel.AHL.value == "ahl"
    assert LeagueLevel.ECHL.value == "echl"


def test_league_level_comparison():
    """Test league level comparison."""
    level = LeagueLevel.NHL
    assert level == LeagueLevel.NHL
    assert level != LeagueLevel.AHL
    assert level in LeagueLevel


def test_league_level_string_behavior():
    """Test that LeagueLevel behaves like a string."""
    level = LeagueLevel.NHL
    assert level.value == "nhl"
    assert isinstance(level.value, str)
    assert level.name == "NHL"


def test_league_level_uniqueness():
    """Test that all league level values are unique."""
    values = [level.value for level in LeagueLevel]
    assert len(values) == len(set(values))
  