"""Module for handling EA NHL Pro Clubs game data requests."""

from typing import Any, Dict, List, Union

from ea_nhl_stats.web.web_request import WebRequest
from ea_nhl_stats.validators.platform_validator import PlatformValidator
from ea_nhl_stats.validators.match_type_validator import MatchTypeValidator

class GetGamesRequest:
    """Handles requests to fetch games data from the EA NHL API.
    
    This class encapsulates the logic for making requests to the EA NHL API
    to fetch games data for a specific club.
    
    Attributes:
        club_id: The ID of the club to fetch games for.
        platform: The gaming platform identifier.
        match_type: The type of match to fetch.
    """
    
    def __init__(
        self,
        club_id: int,
        match_type: str,
        platform: str,
        web_request: WebRequest,
        platform_validator: PlatformValidator,
        match_type_validator: MatchTypeValidator,
    ) -> None:
        """Initialize a new GetGamesRequest instance.
        
        Args:
            club_id: The ID of the club to fetch games for.
            match_type: The type of match to fetch.
            platform: The gaming platform identifier.
            web_request: WebRequest instance for making HTTP requests.
            platform_validator: Validator for platform identifiers.
            match_type_validator: Validator for match types.
            
        Raises:
            ValueError: If any of the validators are None or if platform/match_type are invalid.
        """
        if not web_request:
            raise ValueError("web_request cannot be None")
        if not platform_validator:
            raise ValueError("platform_validator cannot be None")
        if not match_type_validator:
            raise ValueError("match_type_validator cannot be None")
        if not platform_validator.validate(platform):
            raise ValueError(f"Provided value is not a valid platform: {platform}")
        if not match_type_validator.validate(match_type):
            raise ValueError(f"Provided value is not a valid matchType: {match_type}")

        self._club_id = club_id
        self._match_type = match_type
        self._platform = platform
        self._web_request = web_request

    @property
    def club_id(self) -> int:
        """Get the club ID."""
        return self._club_id

    @property
    def platform(self) -> str:
        """Get the platform identifier."""
        return self._platform

    @property
    def match_type(self) -> str:
        """Get the match type."""
        return self._match_type

    @property
    def url(self) -> str:
        """Get the formatted API URL."""
        return f"https://proclubs.ea.com/api/nhl/clubs/matches?clubIds={self.club_id}&platform={self.platform}&matchType={self.match_type}"

    def get_games(self) -> Union[Dict[str, Any], List[Any]]:
        """Fetch games data from the API.
        
        Returns:
            The parsed JSON response from the API.
            
        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
        """
        return self._web_request.process(self.url) 