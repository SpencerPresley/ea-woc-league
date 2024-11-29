"""Tests for club data service."""

from typing import Dict, TYPE_CHECKING
import json
import pytest

from ea_nhl_stats.services.club_data_service import parse_club_data, read_and_parse_club_data

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture

@pytest.fixture(autouse=True)
def setup_logging(caplog: "LogCaptureFixture") -> None:
    """Configure logging for tests."""
    caplog.set_level("INFO")

def test_parse_club_data_valid(club_response_data: Dict, caplog: "LogCaptureFixture") -> None:
    """Test parsing valid club data."""
    club_data = next(iter(club_response_data.values()))
    result = parse_club_data(club_data)
    
    assert result.club_id == 36218
    assert result.name == "JOE NHL"
    assert result.platform == "common-gen5"
    assert "Successfully parsed club data" in caplog.text

def test_parse_club_data_invalid() -> None:
    """Test parsing invalid club data."""
    with pytest.raises(ValueError):
        parse_club_data({})

def test_read_and_parse_club_data_valid(
    club_response_data: Dict,
    tmp_path,
    caplog: "LogCaptureFixture"
) -> None:
    """Test reading and parsing valid club data from file."""
    # Write test data to temp file
    test_file = tmp_path / "test_club_data.json"
    with test_file.open("w") as f:
        json.dump(club_response_data, f)
        
    result = read_and_parse_club_data(str(test_file))
    
    assert result.club_id == 36218
    assert result.name == "JOE NHL"
    assert result.platform == "common-gen5"
    assert "Successfully read club data from file" in caplog.text
    assert "Successfully parsed club data" in caplog.text

def test_read_and_parse_real_club_data(caplog: "LogCaptureFixture") -> None:
    """Test reading and parsing real club data from file."""
    result = read_and_parse_club_data("tests/json/club_response.json")
    
    assert result.club_id == 36218
    assert result.name == "JOE NHL"
    assert result.platform == "common-gen5"
    assert "Successfully read club data from file" in caplog.text
    assert "Successfully parsed club data" in caplog.text

def test_read_and_parse_club_data_file_not_found() -> None:
    """Test reading non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_and_parse_club_data("nonexistent.json")

def test_read_and_parse_club_data_invalid_json(tmp_path) -> None:
    """Test reading invalid JSON file."""
    # Write invalid JSON to temp file
    test_file = tmp_path / "invalid.json"
    with test_file.open("w") as f:
        f.write("invalid json")
        
    with pytest.raises(ValueError):
        read_and_parse_club_data(str(test_file)) 