"""Tests for team identifier enumeration."""

from typing import TYPE_CHECKING

import pytest

from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


def test_team_identifier_values():
    """Test team identifier enum values."""
    assert TeamIdentifier.ST_LOUIS_BLUES.value == "St. Louis Blues"
    assert TeamIdentifier.CALGARY_FLAMES.value == "Calgary Flames"


def test_team_identifier_comparison():
    """Test team identifier comparison."""
    team = TeamIdentifier.ST_LOUIS_BLUES
    assert team == TeamIdentifier.ST_LOUIS_BLUES
    assert team != TeamIdentifier.CALGARY_FLAMES
    assert team in TeamIdentifier


def test_team_identifier_string_behavior():
    """Test that TeamIdentifier behaves like a string."""
    team = TeamIdentifier.ST_LOUIS_BLUES
    assert team.value == "St. Louis Blues"  # Value is the display name
    assert isinstance(team.value, str)  # Value is a string type
    assert team.name == "ST_LOUIS_BLUES"  # Name is the enum key


def test_team_identifier_uniqueness():
    """Test that all team identifier values are unique."""
    values = [team.value for team in TeamIdentifier]
    assert len(values) == len(set(values))  # No duplicates


def test_team_identifier_display_names():
    """Test that display names are properly formatted."""
    for team in TeamIdentifier:
        # Display names should be properly capitalized
        assert team.value[0].isupper()
        # Display names should be human-readable strings
        assert " " in team.value  # Contains spaces
        assert team.value.strip() == team.value  # No leading/trailing whitespace 