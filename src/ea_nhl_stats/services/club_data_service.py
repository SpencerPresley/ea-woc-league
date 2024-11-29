"""Service for handling club data operations."""

import json
import logging
from typing import Dict
from pathlib import Path

from ea_nhl_stats.models.club import ClubData

def parse_club_data(data: Dict) -> ClubData:
    """
    Parse club data from dictionary into ClubData model.
    
    Args:
        data: Dictionary containing club data
        
    Returns:
        ClubData model instance
        
    Raises:
        ValueError: If data is invalid
    """
    try:
        club_data = ClubData.model_validate(data)
        logging.info("Successfully parsed club data")
        return club_data
    except Exception as e:
        logging.error(f"Error parsing club data: {e}")
        raise ValueError(f"Invalid club data: {e}")

def read_and_parse_club_data(file_path: str) -> ClubData:
    """
    Read club data from JSON file and parse into ClubData model.
    
    Args:
        file_path: Path to JSON file containing club data
        
    Returns:
        ClubData model instance
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is invalid or data is invalid
    """
    path = Path(file_path)
    if not path.exists():
        logging.error(f"Error: File '{file_path}' not found")
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        with path.open() as f:
            data = json.load(f)
        logging.info("Successfully read club data from file")
        
        # Extract first club from response
        club_data = next(iter(data.values()))
        return parse_club_data(club_data)
    except json.JSONDecodeError as e:
        logging.error(f"Error: Invalid JSON in file {file_path}: {e}")
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error reading/parsing club data: {e}")
        raise 