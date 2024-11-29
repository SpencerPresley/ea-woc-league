from typing import Dict, TYPE_CHECKING
import pytest
from ea_nhl_stats.models.club import ClubData, ClubInfo, CustomKit

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

def test_club_data_from_dict(club_response_data: Dict) -> None:
    """Test creating a ClubData object from a dictionary."""
    club_data = next(iter(club_response_data.values()))
    data = ClubData.model_validate(club_data)
    
    assert data.club_id == 36218
    assert data.name == "JOE NHL"
    assert data.platform == "common-gen5"
    assert data.recent_score0 == "5-3"
    assert data.recent_score1 == "7-4"
    assert isinstance(data.club_info, ClubInfo)
    assert isinstance(data.club_info.custom_kit, CustomKit)

def test_club_data_to_dict(club_response_data: Dict) -> None:
    """Test converting a ClubData object to a dictionary."""
    club_data = next(iter(club_response_data.values()))
    data = ClubData.model_validate(club_data)
    dict_data = data.model_dump(by_alias=True)
    
    assert dict_data["clubId"] == 36218
    assert dict_data["name"] == "JOE NHL"
    assert dict_data["platform"] == "common-gen5"
    assert dict_data["recentScore0"] == "5-3"
    assert dict_data["recentScore1"] == "7-4"
    assert isinstance(dict_data["clubInfo"], dict)