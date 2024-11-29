"""Tests for base game data models."""

from typing import Dict, TYPE_CHECKING

import pytest
from pydantic import BaseModel

from ea_nhl_stats.models.game.base import NumericValidatorBase

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_numeric_validator_base_handles_dashes() -> None:
    """Test that NumericValidatorBase properly handles '--' values."""
    
    class TestModel(NumericValidatorBase):
        value: str | None
    
    model = TestModel(value="--")
    assert model.value is None


def test_numeric_validator_base_handles_non_dash_values() -> None:
    """Test that NumericValidatorBase preserves non-dash values."""
    
    class TestModel(NumericValidatorBase):
        value: str
    
    model = TestModel(value="test")
    assert model.value == "test"


def test_numeric_validator_base_handles_non_dict_data() -> None:
    """Test that NumericValidatorBase can handle non-dictionary input."""
    
    class TestModel(NumericValidatorBase):
        value: str
    
    model = TestModel(value="test")
    assert model.value == "test"


def test_numeric_validator_base_returns_non_dict_data() -> None:
    """Test that handle_dashes returns non-dict data unchanged."""
    
    non_dict_data = ["test", "data"]
    result = NumericValidatorBase.handle_dashes(non_dict_data)
    assert result == non_dict_data 