"""Tests for team implementations."""

from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.models.teams.implementations import (
    StLouisBlues,
    CalgaryFlames
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


def test_st_louis_blues_initialization():
    """Test St. Louis Blues team initialization."""
    team = StLouisBlues()
    assert team.official_name == TeamIdentifier.ST_LOUIS_BLUES.value
    assert team.league_level == LeagueLevel.NHL


def test_st_louis_blues_with_data():
    """Test St. Louis Blues team initialization with additional data."""
    ea_club_id = "123"
    ea_club_name = "Test Blues"
    team = StLouisBlues(
        ea_club_id=ea_club_id,
        ea_club_name=ea_club_name
    )
    assert team.official_name == TeamIdentifier.ST_LOUIS_BLUES.value
    assert team.league_level == LeagueLevel.NHL
    assert team.ea_club_id == ea_club_id
    assert team.ea_club_name == ea_club_name


def test_calgary_flames_initialization():
    """Test Calgary Flames team initialization."""
    team = CalgaryFlames()
    assert team.official_name == TeamIdentifier.CALGARY_FLAMES.value
    assert team.league_level == LeagueLevel.NHL


def test_calgary_flames_with_data():
    """Test Calgary Flames team initialization with additional data."""
    ea_club_id = "456"
    ea_club_name = "Test Flames"
    team = CalgaryFlames(
        ea_club_id=ea_club_id,
        ea_club_name=ea_club_name
    )
    assert team.official_name == TeamIdentifier.CALGARY_FLAMES.value
    assert team.league_level == LeagueLevel.NHL
    assert team.ea_club_id == ea_club_id
    assert team.ea_club_name == ea_club_name 