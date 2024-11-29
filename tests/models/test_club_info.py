"""Tests for club info models."""

from typing import Dict, TYPE_CHECKING
import pytest
from ea_nhl_stats.models.club import ClubInfo, CustomKit, ClubData

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

def test_custom_kit_valid(club_response_data: Dict) -> None:
    """Test CustomKit model with valid data."""
    club_data = next(iter(club_response_data.values()))
    custom_kit_data = club_data["clubInfo"]["customKit"]
    custom_kit = CustomKit.model_validate(custom_kit_data)
    
    assert custom_kit.is_custom_team == 1
    assert custom_kit.crest_asset_id == "348"
    assert custom_kit.use_base_asset == 0

def test_club_info_valid(club_response_data: Dict) -> None:
    """Test ClubInfo model with valid data."""
    club_data = next(iter(club_response_data.values()))
    club_info_data = club_data["clubInfo"]
    club_info = ClubInfo.model_validate(club_info_data)
    
    assert club_info.name == "JOE NHL"
    assert club_info.club_id == 36218
    assert club_info.region_id == 5
    assert club_info.team_id == 264
    assert isinstance(club_info.custom_kit, CustomKit)

def test_club_data_valid(club_response_data: Dict) -> None:
    """Test ClubData model with valid data."""
    club_data = next(iter(club_response_data.values()))
    data = ClubData.model_validate(club_data)
    
    assert data.club_id == 36218
    assert data.name == "JOE NHL"
    assert data.platform == "common-gen5"
    assert data.recent_score0 == "5-3"
    assert data.recent_score1 == "7-4"
    assert isinstance(data.club_info, ClubInfo) 