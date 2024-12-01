"""Tests for the SeasonBuilder."""

from typing import TYPE_CHECKING

import pytest
from pytest_mock.plugin import MockerFixture

from ea_nhl_stats.league.models.season import Season, SeasonBuilder
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def builder() -> SeasonBuilder:
    """Create a test builder."""
    return SeasonBuilder()


def test_builder_initialization() -> None:
    """Test that builder initializes correctly."""
    builder = SeasonBuilder()
    assert builder._season_id is None
    assert isinstance(builder._tiers, dict)
    assert len(builder._tiers) == 0


def test_with_season_id(builder: SeasonBuilder) -> None:
    """Test setting season ID."""
    builder.with_season_id("2024")
    assert builder._season_id == "2024"


def test_with_tier_nhl(builder: SeasonBuilder) -> None:
    """Test adding NHL tier with its teams."""
    builder.with_tier(LeagueLevel.NHL)
    
    # Should have NHL teams
    tier = builder._tiers[LeagueLevel.NHL]
    assert TeamIdentifier.ST_LOUIS_BLUES in tier.teams
    assert TeamIdentifier.CALGARY_FLAMES in tier.teams
    
    # Teams should be properly initialized
    blues = tier.teams[TeamIdentifier.ST_LOUIS_BLUES]
    assert blues.official_name == TeamIdentifier.ST_LOUIS_BLUES.value
    assert blues.league_level == LeagueLevel.NHL


def test_build_without_season_id(builder: SeasonBuilder) -> None:
    """Test that building without season ID raises error."""
    builder.with_tier(LeagueLevel.NHL)
    with pytest.raises(ValueError, match="Season ID must be set"):
        builder.build()


def test_build_complete_season(builder: SeasonBuilder) -> None:
    """Test building a complete season."""
    season = (builder
        .with_season_id("2024")
        .with_tier(LeagueLevel.NHL)
        .build()
    )
    
    assert isinstance(season, Season)
    assert season.season_id == "2024"
    assert LeagueLevel.NHL in season.tiers
    
    # Should have NHL teams
    nhl_tier = season.tiers[LeagueLevel.NHL]
    assert TeamIdentifier.ST_LOUIS_BLUES in nhl_tier.teams
    assert TeamIdentifier.CALGARY_FLAMES in nhl_tier.teams


def test_build_multiple_tiers(builder: SeasonBuilder) -> None:
    """Test building with multiple tiers."""
    season = (builder
        .with_season_id("2024")
        .with_tier(LeagueLevel.NHL)
        .with_tier(LeagueLevel.AHL)
        .build()
    )
    
    assert LeagueLevel.NHL in season.tiers
    assert LeagueLevel.AHL in season.tiers
    
    # NHL should have teams, AHL should be empty
    assert len(season.tiers[LeagueLevel.NHL].teams) > 0
    assert len(season.tiers[LeagueLevel.AHL].teams) == 0


def test_builder_reuse(builder: SeasonBuilder) -> None:
    """Test that builder can be reused."""
    # Build first season
    season1 = (builder
        .with_season_id("2024")
        .with_tier(LeagueLevel.NHL)
        .build()
    )
    
    # Build second season
    season2 = (builder
        .with_season_id("2025")
        .with_tier(LeagueLevel.NHL)
        .build()
    )
    
    assert season1.season_id == "2024"
    assert season2.season_id == "2025"
    assert season1 is not season2
    
    # Teams should be different instances
    team1 = season1.tiers[LeagueLevel.NHL].teams[TeamIdentifier.ST_LOUIS_BLUES]
    team2 = season2.tiers[LeagueLevel.NHL].teams[TeamIdentifier.ST_LOUIS_BLUES]
    assert team1 is not team2 