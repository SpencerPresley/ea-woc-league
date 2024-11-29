"""Shared pytest fixtures for testing."""

from typing import Dict, List
from pathlib import Path
import os
import json
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture
    

# Get the directory where conftest.py is located
TEST_DIR = Path(__file__).parent
# Define the directory containing the JSON test data
JSON_DIR = TEST_DIR / "json"

@pytest.fixture
def club_response_data() -> Dict:
    """
    Fixture providing sample club response data.
    
    Returns:
        Dictionary containing club response data from the NHL API
    """
    json_path = JSON_DIR / "club_response.json"
    with json_path.open("r") as f:
        return json.load(f)

@pytest.fixture
def club_id(club_response_data: Dict) -> str:
    """
    Fixture providing a sample club ID.
    
    Returns:
        String containing a valid club ID from the test data
    """
    return next(iter(club_response_data.keys()))

@pytest.fixture
def game_response_data() -> List[Dict]:
    """
    Fixture providing sample game response data.
    
    Returns:
        List of dictionaries containing game response data from the NHL API
    """
    json_path = JSON_DIR / "response.json"
    with json_path.open("r") as f:
        return json.load(f)