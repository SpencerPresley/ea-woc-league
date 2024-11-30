"""Tests for team factory."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.factories.team_factory import TeamFactory
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def clear_factory():
    """Fixture to clear factory registrations between tests."""
    original_teams = TeamFactory._teams.copy()
    TeamFactory._teams.clear()
    yield
    TeamFactory._teams = original_teams


@pytest.fixture
def mock_team_class():
    """Fixture providing a mock team class."""
    class MockTeam(LeagueTeam):
        def __init__(self, **data):
            super().__init__(
                official_name="Mock Team",
                league_level=LeagueLevel.NHL,
                **data
            )
    return MockTeam


def test_team_factory_registration(clear_factory, mock_team_class):
    """Test team registration with factory."""
    # Register a mock team
    identifier = TeamIdentifier.ST_LOUIS_BLUES
    decorated_class = TeamFactory.register(identifier)(mock_team_class)
    
    # Verify registration
    assert decorated_class == mock_team_class
    assert TeamFactory._teams[identifier] == mock_team_class


def test_team_factory_create(clear_factory, mock_team_class):
    """Test team creation through factory."""
    # Register the mock team first
    identifier = TeamIdentifier.ST_LOUIS_BLUES
    TeamFactory.register(identifier)(mock_team_class)
    
    # Create a team instance
    team = TeamFactory.create(identifier)
    assert isinstance(team, LeagueTeam)
    assert isinstance(team, mock_team_class)
    assert team.official_name == "Mock Team"  # Uses mock team's name
    assert team.league_level == LeagueLevel.NHL


def test_team_factory_create_with_kwargs(clear_factory, mock_team_class):
    """Test team creation with additional kwargs."""
    # Register the mock team first
    identifier = TeamIdentifier.ST_LOUIS_BLUES
    TeamFactory.register(identifier)(mock_team_class)
    
    # Create with valid team fields
    ea_club_id = "12345"  # String type
    ea_club_name = "Test Club"
    team = TeamFactory.create(
        identifier,
        ea_club_id=ea_club_id,
        ea_club_name=ea_club_name
    )
    assert isinstance(team, LeagueTeam)
    assert team.ea_club_id == ea_club_id
    assert team.ea_club_name == ea_club_name


def test_team_factory_unregistered_identifier():
    """Test factory behavior with unregistered team identifier."""
    # Try to create a team that isn't registered
    with pytest.raises(ValueError) as exc_info:
        TeamFactory.create(TeamIdentifier.CALGARY_FLAMES)
    
    assert "No implementation for team" in str(exc_info.value) 