"""Tests for the WebRequest class."""

from typing import TYPE_CHECKING
import pytest
import requests
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

def test_process_successful_request(
    web_request: WebRequest,
    mocker: "MockerFixture"
) -> None:
    """Test successful API request processing."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_response.status_code = 200
    mock_response.text = '{"data": "test"}'
    
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    result = web_request.process("https://test.com/api")
    
    assert result == {"data": "test"}
    mock_get.assert_called_once_with(
        "https://test.com/api",
        headers={"User-Agent": "Mozilla/5.0 (compatible; MyTestClient/1.0)"},
        timeout=10
    )

def test_process_failed_request(
    web_request: WebRequest,
    mocker: "MockerFixture"
) -> None:
    """Test failed API request processing."""
    mock_get = mocker.patch('requests.get', side_effect=requests.RequestException("Test error"))
    
    with pytest.raises(requests.RequestException, match="Test error"):
        web_request.process("https://test.com/api") 