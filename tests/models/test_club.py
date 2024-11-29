"""Tests for club data models."""

from typing import Dict, TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.club import CustomKit, ClubInfo, ClubData, ClubResponse

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_custom_kit_model(club_response_data: Dict, club_id: str) -> None:
    """
    Test CustomKit model validation and data conversion.
    
    Args:
        club_response_data: Sample club response data
        club_id: Sample club ID
    """
    custom_kit_data = club_response_data[club_id]["clubInfo"]["customKit"]
    custom_kit = CustomKit.model_validate(custom_kit_data)
    
    assert custom_kit.is_custom_team == 1
    assert isinstance(custom_kit.is_custom_team, int)
    assert isinstance(custom_kit.crest_asset_id, str)
    assert isinstance(custom_kit.use_base_asset, int)


def test_club_info_model(club_response_data: Dict, club_id: str) -> None:
    """
    Test ClubInfo model validation and data conversion.
    
    Args:
        club_response_data: Sample club response data
        club_id: Sample club ID
    """
    club_info_data = club_response_data[club_id]["clubInfo"]
    club_info = ClubInfo.model_validate(club_info_data)
    
    assert club_info.name == "JOE NHL"
    assert club_info.club_id == 36218
    assert isinstance(club_info.region_id, int)
    assert isinstance(club_info.team_id, int)
    assert isinstance(club_info.custom_kit, CustomKit)


def test_club_data_model(club_response_data: Dict, club_id: str) -> None:
    """
    Test ClubData model validation and data conversion.
    
    Args:
        club_response_data: Sample club response data
        club_id: Sample club ID
    """
    club_data = club_response_data[club_id]
    club = ClubData.model_validate(club_data)
    
    # Test basic information
    assert club.name == "JOE NHL"
    assert club.club_id == 36218
    assert club.platform == "common-gen5"
    
    # Test statistics
    assert isinstance(club.wins, int)
    assert isinstance(club.losses, int)
    assert isinstance(club.ties, int)
    assert isinstance(club.goals, int)
    assert isinstance(club.goals_against, int)
    
    # Test nested club info
    assert isinstance(club.club_info, ClubInfo)
    assert club.club_info.name == club.name
    assert club.club_info.club_id == club.club_id


def test_club_response_model(club_response_data: Dict) -> None:
    """
    Test ClubResponse model validation and data conversion.
    
    Args:
        club_response_data: Sample club response data
    """
    response = ClubResponse.model_validate(club_response_data)
    
    assert len(response.root) == 1
    club_id = next(iter(response.root))
    assert isinstance(response.root[club_id], ClubData)


def test_invalid_club_data() -> None:
    """Test validation errors for invalid club data."""
    invalid_data = {
        "name": "Test Club",
        "clubId": "not_an_int",  # Should be convertible to int
        "wins": "not_an_int",    # Should be convertible to int
        "platform": 123,         # Should be string
    }
    
    with pytest.raises(ValidationError):
        ClubData.model_validate(invalid_data)


def test_invalid_score_format(club_response_data: Dict, club_id: str) -> None:
    """Test validation error for invalid score format."""
    # Start with valid data
    valid_data = club_response_data[club_id].copy()
    # Modify just the recent score field to be invalid
    valid_data["recentScore0"] = "123"  # Invalid format, should be "int-int"
    
    with pytest.raises(ValidationError, match="Score must be in the format 'int-int'"):
        ClubData.model_validate(valid_data) 