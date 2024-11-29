"""
Utility functions for parsing club data from JSON responses.

This module provides functions to parse and validate club data from JSON responses
from the EA NHL Pro Clubs API.
"""

import json
from typing import Dict, Optional

from pydantic import ValidationError

from ea_nhl_stats.models.club import ClubData


def parse_club_data(json_data: Dict) -> Optional[Dict[str, ClubData]]:
    """
    Parse raw JSON data into ClubData objects.
    
    Args:
        json_data: Raw JSON data containing club information
        
    Returns:
        Dictionary mapping club IDs to ClubData objects, or None if parsing fails
        
    Example:
        >>> with open("club_data.json") as f:
        ...     data = json.load(f)
        >>> clubs = parse_club_data(data)
        >>> if clubs:
        ...     print(f"Parsed {len(clubs)} clubs")
    """
    try:
        return {
            club_id: ClubData.model_validate(club_data)
            for club_id, club_data in json_data.items()
        }
    except ValidationError as e:
        print(f"Error parsing JSON: {e}")
        return None


def read_and_parse_club_data(filepath: str) -> Optional[Dict[str, ClubData]]:
    """
    Read club data from a JSON file and parse it.
    
    Args:
        filepath: Path to the JSON file containing club data
        
    Returns:
        Dictionary mapping club IDs to ClubData objects, or None if parsing fails
        
    Example:
        >>> clubs = read_and_parse_club_data("club_response.json")
        >>> if clubs:
        ...     for club_id, club_data in clubs.items():
        ...         print(f"Club {club_id}: {club_data.name}")
    """
    try:
        with open(filepath, "r") as f:
            json_data = json.load(f)
            return parse_club_data(json_data)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return None 