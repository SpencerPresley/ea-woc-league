"""Tests for club data parsing utilities."""

import json
import tempfile
from pathlib import Path
from typing import Dict, TYPE_CHECKING

import pytest

from ea_nhl_stats.models.club import ClubData
from ea_nhl_stats.utils.club_parser import parse_club_data, read_and_parse_club_data

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_parse_club_data(club_response_data: Dict) -> None:
    """
    Test parsing of club data from JSON.
    
    Args:
        club_response_data: Sample club response data
    """
    result = parse_club_data(club_response_data)
    
    assert result is not None
    assert len(result) == 1
    
    club_id = next(iter(result))
    club = result[club_id]
    
    assert isinstance(club, ClubData)
    assert club.name == "JOE NHL"
    assert club.club_id == 36218


def test_parse_club_data_invalid() -> None:
    """Test parsing of invalid club data."""
    invalid_data = {
        "12345": {
            "name": "Test Club",
            "clubId": "not_an_int",
            "wins": "not_an_int",
        }
    }
    
    result = parse_club_data(invalid_data)
    assert result is None


def test_read_and_parse_club_data(club_response_data: Dict) -> None:
    """
    Test reading and parsing club data from a file.
    
    Args:
        club_response_data: Sample club response data
    """
    # Create a temporary file with test data
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(club_response_data, f)
        temp_file = Path(f.name)
    
    try:
        result = read_and_parse_club_data(str(temp_file))
        
        assert result is not None
        assert len(result) == 1
        
        club_id = next(iter(result))
        club = result[club_id]
        
        assert isinstance(club, ClubData)
        assert club.name == "JOE NHL"
        assert club.club_id == 36218
    
    finally:
        # Clean up the temporary file
        temp_file.unlink()


def test_read_and_parse_club_data_file_not_found() -> None:
    """Test handling of non-existent file."""
    result = read_and_parse_club_data("nonexistent_file.json")
    assert result is None


def test_read_and_parse_club_data_invalid_json() -> None:
    """Test handling of invalid JSON file."""
    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json content")
        temp_file = Path(f.name)
    
    try:
        result = read_and_parse_club_data(str(temp_file))
        assert result is None
    
    finally:
        # Clean up the temporary file
        temp_file.unlink() 