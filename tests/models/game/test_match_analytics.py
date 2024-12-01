"""Tests for match analytics functionality."""

from typing import TYPE_CHECKING, List
import json
import pytest
from ea_nhl_stats.models.game.match_analytics import MatchAnalytics
from ea_nhl_stats.models.game.ea_match import Match

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def ea_response_data():
    """Load test EA API response data."""
    with open("live_tests/output/ea_response.json") as f:
        return json.load(f)


@pytest.fixture
def matches(ea_response_data) -> List[Match]:
    """Create test matches from EA API data."""
    return [Match.model_validate(match_data) for match_data in ea_response_data]


def test_match_analytics(matches):
    """Test match analytics functionality."""
    analytics = MatchAnalytics(matches)
    
    # Test basic analytics
    assert len(analytics.matches) > 0
    assert isinstance(analytics.matches[0], Match)
    
    # Test club stats
    club_stats = analytics.get_club_stats("1789")  # LG Blues
    assert club_stats is not None
    assert club_stats.goals > 0
    assert club_stats.shots > 0
    
    # Test player stats
    player_stats = analytics.get_player_stats("1789", "1669236396")  # vViperrz
    assert player_stats is not None
    assert player_stats.skgoals > 0
    assert player_stats.skshots > 0 