"""Tests for club and match models."""

from typing import Dict, List, TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.club import (
    Club,
    CustomKit,
    Details,
    Match,
    TimeAgo,
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_custom_kit_model(game_response_data: List[Dict]) -> None:
    """
    Test CustomKit model validation and data conversion.
    
    Args:
        game_response_data: Sample game response data
    """
    first_club_id = next(iter(game_response_data[0]["clubs"]))
    custom_kit_data = game_response_data[0]["clubs"][first_club_id]["details"]["customKit"]
    
    custom_kit = CustomKit.model_validate(custom_kit_data)
    
    assert isinstance(custom_kit.is_custom_team, int)
    assert isinstance(custom_kit.crest_asset_id, str)
    assert isinstance(custom_kit.use_base_asset, int)


def test_details_model(game_response_data: List[Dict]) -> None:
    """
    Test Details model validation and data conversion.
    
    Args:
        game_response_data: Sample game response data
    """
    first_club_id = next(iter(game_response_data[0]["clubs"]))
    details_data = game_response_data[0]["clubs"][first_club_id]["details"]
    
    details = Details.model_validate(details_data)
    
    assert isinstance(details.name, str)
    assert isinstance(details.club_id, int)
    assert isinstance(details.region_id, int)
    assert isinstance(details.team_id, int)
    assert isinstance(details.custom_kit, CustomKit)


def test_club_model(game_response_data: List[Dict]) -> None:
    """
    Test Club model validation and data conversion.
    
    Args:
        game_response_data: Sample game response data
    """
    first_club_id = next(iter(game_response_data[0]["clubs"]))
    club_data = game_response_data[0]["clubs"][first_club_id]
    
    club = Club.model_validate(club_data)
    
    # Test basic information
    assert isinstance(club.club_division, str)
    
    # Test game type
    assert isinstance(club.cnhl_online_game_type, str)
    
    # Test game results
    assert isinstance(club.goals_against_raw, str)
    assert isinstance(club.goals_for_raw, str)
    assert isinstance(club.losses, str)
    assert isinstance(club.result, str)
    assert isinstance(club.score, str)
    assert isinstance(club.score_string, str)
    assert isinstance(club.winner_by_dnf, str)
    assert isinstance(club.winner_by_goalie_dnf, str)
    
    # Test team stats
    assert isinstance(club.member_string, str)
    assert isinstance(club.passes_attempted, str)
    assert isinstance(club.passes_completed, str)
    assert isinstance(club.powerplay_goals, str)
    assert isinstance(club.powerplay_opportunities, str)
    assert isinstance(club.shots, str)
    assert isinstance(club.team_art_abbr, str)
    assert isinstance(club.team_side, str)
    assert isinstance(club.time_on_attack, str)
    
    # Test opponent info
    assert isinstance(club.opponent_club_id, str)
    assert isinstance(club.opponent_score, str)
    assert isinstance(club.opponent_team_art_abbr, str)
    
    # Test club details
    assert isinstance(club.details, Details)
    assert isinstance(club.goals, str)
    assert isinstance(club.goals_against, str)


def test_time_ago_model(game_response_data: List[Dict]) -> None:
    """
    Test TimeAgo model validation and data conversion.
    
    Args:
        game_response_data: Sample game response data
    """
    time_ago_data = game_response_data[0]["timeAgo"]
    
    time_ago = TimeAgo.model_validate(time_ago_data)
    
    assert isinstance(time_ago.number, int)
    assert isinstance(time_ago.unit, str)


def test_match_model(game_response_data: List[Dict]) -> None:
    """
    Test Match model validation and data conversion.
    
    Args:
        game_response_data: Sample game response data
    """
    match_data = game_response_data[0]
    
    match = Match.model_validate(match_data)
    
    assert isinstance(match.match_id, str)
    assert isinstance(match.timestamp, int)
    assert isinstance(match.time_ago, TimeAgo)
    assert isinstance(match.clubs, dict)
    assert isinstance(match.players, dict)
    assert isinstance(match.aggregate, dict)


def test_invalid_club_data() -> None:
    """Test validation errors for invalid club data."""
    invalid_data = {
        "clubDivision": 123,  # Should be str
        "garaw": 123,         # Should be str
        "details": {          # Missing required fields
            "name": "Test Club"
        }
    }
    
    with pytest.raises(ValidationError):
        Club.model_validate(invalid_data)


def test_invalid_match_data() -> None:
    """Test validation errors for invalid match data."""
    invalid_data = {
        "matchId": 123,       # Should be str
        "timestamp": "123",   # Should be int
        "timeAgo": {          # Missing required fields
            "number": 5
        }
    }
    
    with pytest.raises(ValidationError):
        Match.model_validate(invalid_data) 