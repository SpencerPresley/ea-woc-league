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
def test_match(ea_response_data) -> Match:
    """Create test match from EA API data."""
    return Match.model_validate(ea_response_data[0])


def test_match_analytics(test_match):
    """Test match analytics functionality."""
    analytics = MatchAnalytics(test_match)
    
    # Test possession metrics
    possession = analytics.get_possession_metrics()
    assert possession is not None
    assert isinstance(possession.possession_differential, float)
    assert isinstance(possession.possession_percentage_home, float)
    assert isinstance(possession.possession_percentage_away, float)
    
    # Test efficiency metrics
    efficiency = analytics.get_efficiency_metrics()
    assert efficiency is not None
    assert isinstance(efficiency.home_shooting_efficiency, float)
    assert isinstance(efficiency.away_shooting_efficiency, float)
    
    # Test special teams metrics
    special_teams = analytics.get_special_teams_metrics()
    assert special_teams is not None
    assert isinstance(special_teams.home_powerplay_pct, float)
    assert isinstance(special_teams.away_powerplay_pct, float)
    
    # Test momentum metrics
    momentum = analytics.get_momentum_metrics()
    assert momentum is not None
    assert isinstance(momentum.shot_differential, int)
    assert isinstance(momentum.hit_differential, int) 