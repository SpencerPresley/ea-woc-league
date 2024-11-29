"""Tests for match analytics functionality."""

from typing import TYPE_CHECKING, List
import json
import pytest
from ea_nhl_stats.models.game.match_analytics import MatchAnalytics
from ea_nhl_stats.models.game.ea_match import Match
from live_tests.track_stats import load_matches

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def matches() -> List[Match]:
    """Load matches using track_stats process."""
    return load_matches()


@pytest.fixture
def sample_match(matches: List[Match]) -> Match:
    """Get first match from loaded matches."""
    return matches[0]


def test_possession_metrics(sample_match: Match) -> None:
    """Test possession metrics calculation."""
    analytics = MatchAnalytics(sample_match)
    metrics = analytics.get_possession_metrics()
    
    assert metrics is not None
    assert metrics.possession_differential == -147  # Home: 421, Away: 596
    assert pytest.approx(metrics.possession_percentage_home, rel=1e-2) == 46.65  # 421 / (421 + 596) * 100
    assert pytest.approx(metrics.possession_percentage_away, rel=1e-2) == 53.35  # 596 / (421 + 596) * 100
    assert metrics.time_on_attack_differential == -175  # 421 - 596


def test_efficiency_metrics(sample_match: Match) -> None:
    """Test efficiency metrics calculation."""
    analytics = MatchAnalytics(sample_match)
    metrics = analytics.get_efficiency_metrics()
    
    assert metrics is not None
    assert pytest.approx(metrics.home_shooting_efficiency, rel=1e-2) == 45.45  # 10/22 * 100
    assert pytest.approx(metrics.away_shooting_efficiency, rel=1e-2) == 42.31  # 11/26 * 100
    assert pytest.approx(metrics.home_passing_efficiency, rel=1e-2) == 78.35  # 76/97 * 100
    assert pytest.approx(metrics.away_passing_efficiency, rel=1e-2) == 71.88  # 69/96 * 100


def test_special_teams_metrics(sample_match: Match) -> None:
    """Test special teams metrics calculation."""
    analytics = MatchAnalytics(sample_match)
    metrics = analytics.get_special_teams_metrics()
    
    assert metrics is not None
    assert pytest.approx(metrics.home_powerplay_pct) == 75.0  # 3/4 * 100
    assert pytest.approx(metrics.away_powerplay_pct) == 50.0  # 2/4 * 100
    assert pytest.approx(metrics.home_penalty_kill_pct) == 50.0  # 2 goals against on 4 opportunities
    assert pytest.approx(metrics.away_penalty_kill_pct) == 25.0  # 3 goals against on 4 opportunities


def test_momentum_metrics(sample_match: Match) -> None:
    """Test momentum metrics calculation."""
    analytics = MatchAnalytics(sample_match)
    metrics = analytics.get_momentum_metrics()
    
    assert metrics is not None
    assert metrics.shot_differential == -5  # 22 - 27
    
    # Get hits from player stats
    home_hits = sum(int(p.skhits) for p in sample_match.players["1789"].values())
    away_hits = sum(int(p.skhits) for p in sample_match.players["45048"].values())
    assert metrics.hit_differential == home_hits - away_hits
    
    # Get takeaways/giveaways from player stats
    home_takeaways = sum(int(p.sktakeaways) for p in sample_match.players["1789"].values())
    home_giveaways = sum(int(p.skgiveaways) for p in sample_match.players["1789"].values())
    away_takeaways = sum(int(p.sktakeaways) for p in sample_match.players["45048"].values())
    away_giveaways = sum(int(p.skgiveaways) for p in sample_match.players["45048"].values())
    
    assert metrics.takeaway_differential == (home_takeaways - home_giveaways) - (away_takeaways - away_giveaways)


def test_get_all_metrics(sample_match: Match) -> None:
    """Test retrieving all metrics at once."""
    analytics = MatchAnalytics(sample_match)
    all_metrics = analytics.get_all_metrics()
    
    assert all_metrics["possession"] is not None
    assert all_metrics["efficiency"] is not None
    assert all_metrics["special_teams"] is not None
    assert all_metrics["momentum"] is not None


def test_handle_missing_data(mocker: "MockerFixture") -> None:
    """Test graceful handling of missing data."""
    # Create match with missing data
    with open("live_tests/output/ea_response.json") as f:
        data = json.load(f)
        match_data = data[0].copy()
        
        # Remove required data
        match_data["clubs"] = {}
        match_data["players"] = {}
        match_data["aggregate"] = {}  # Empty dict instead of list
        
        match = Match.model_validate(match_data)
    
    analytics = MatchAnalytics(match)
    
    assert analytics.get_possession_metrics() is None
    assert analytics.get_efficiency_metrics() is None
    assert analytics.get_special_teams_metrics() is None
    assert analytics.get_momentum_metrics() is None 