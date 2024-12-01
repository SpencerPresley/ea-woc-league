"""Tests for the Season model."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pytest_mock.plugin import MockerFixture

from ea_nhl_stats.league.models.season import Season, TierData
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer
from ea_nhl_stats.league.enums.types import Position

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def season() -> Season:
    """Create a test season."""
    return Season(season_id="2024", tiers={})


@pytest.fixture
def tier_data() -> TierData:
    """Create a test tier."""
    return TierData()


def test_season_initialization() -> None:
    """Test that Season initializes correctly."""
    season = Season(season_id="2024", tiers={})
    
    assert season.season_id == "2024"
    assert isinstance(season.tiers, dict)
    assert len(season.tiers) == 0


def test_season_add_tier(season: Season, tier_data: TierData) -> None:
    """Test adding a tier to a season."""
    season.tiers[LeagueLevel.NHL] = tier_data
    assert season.tiers[LeagueLevel.NHL] == tier_data


def test_season_get_nonexistent_tier(season: Season) -> None:
    """Test getting a tier that doesn't exist raises KeyError."""
    with pytest.raises(KeyError):
        _ = season.tiers[LeagueLevel.NHL]


def test_season_multiple_tiers(season: Season, tier_data: TierData) -> None:
    """Test adding multiple tiers to a season."""
    nhl_tier = TierData()
    ahl_tier = TierData()
    
    season.tiers[LeagueLevel.NHL] = nhl_tier
    season.tiers[LeagueLevel.AHL] = ahl_tier
    
    assert season.tiers[LeagueLevel.NHL] == nhl_tier
    assert season.tiers[LeagueLevel.AHL] == ahl_tier
    assert season.tiers[LeagueLevel.NHL] is not season.tiers[LeagueLevel.AHL] 