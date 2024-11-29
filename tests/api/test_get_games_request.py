"""Tests for the get games request module."""

from typing import Any, Dict, List, Union
from typing import TYPE_CHECKING
import pytest
from ea_nhl_stats.api.get_games_request import GetGamesRequest
from ea_nhl_stats.validators.platform_validator import PlatformValidator
from ea_nhl_stats.validators.match_type_validator import MatchTypeValidator
from ea_nhl_stats.web.web_request import WebRequest

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def web_request() -> WebRequest:
    """Fixture providing a WebRequest instance."""
    return WebRequest()

@pytest.fixture
def platform_validator() -> PlatformValidator:
    """Fixture providing a PlatformValidator instance."""
    return PlatformValidator()

@pytest.fixture
def match_type_validator() -> MatchTypeValidator:
    """Fixture providing a MatchTypeValidator instance."""
    return MatchTypeValidator()

def test_get_games_request_initialization(
    web_request: WebRequest,
    platform_validator: PlatformValidator,
    match_type_validator: MatchTypeValidator,
) -> None:
    """Test successful initialization of GetGamesRequest."""
    request = GetGamesRequest(
        club_id=36218,
        match_type="gameType5",
        platform="common-gen5",
        web_request=web_request,
        platform_validator=platform_validator,
        match_type_validator=match_type_validator,
    )
    
    assert request.club_id == 36218
    assert request.match_type == "gameType5"
    assert request.platform == "common-gen5"

def test_get_games_request_invalid_platform(
    web_request: WebRequest,
    platform_validator: PlatformValidator,
    match_type_validator: MatchTypeValidator,
) -> None:
    """Test initialization with invalid platform raises ValueError."""
    with pytest.raises(ValueError, match="Provided value is not a valid platform"):
        GetGamesRequest(
            club_id=36218,
            match_type="gameType5",
            platform="invalid",
            web_request=web_request,
            platform_validator=platform_validator,
            match_type_validator=match_type_validator,
        )

def test_get_games_request_invalid_match_type(
    web_request: WebRequest,
    platform_validator: PlatformValidator,
    match_type_validator: MatchTypeValidator,
) -> None:
    """Test initialization with invalid match type raises ValueError."""
    with pytest.raises(ValueError, match="Provided value is not a valid matchType"):
        GetGamesRequest(
            club_id=36218,
            match_type="invalid",
            platform="common-gen5",
            web_request=web_request,
            platform_validator=platform_validator,
            match_type_validator=match_type_validator,
        )

def test_get_games_request_url_formation(
    web_request: WebRequest,
    platform_validator: PlatformValidator,
    match_type_validator: MatchTypeValidator,
) -> None:
    """Test correct URL formation."""
    request = GetGamesRequest(
        club_id=36218,
        match_type="gameType5",
        platform="common-gen5",
        web_request=web_request,
        platform_validator=platform_validator,
        match_type_validator=match_type_validator,
    )
    
    expected_url = "https://proclubs.ea.com/api/nhl/clubs/matches?clubIds=36218&platform=common-gen5&matchType=gameType5"
    assert request.url == expected_url