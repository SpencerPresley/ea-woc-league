"""Tests for participant history tracking."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.enums.league_types import ManagerRole
from ea_nhl_stats.league.models.player_history import (
    TransactionType,
    Transaction,
    ContractHistory,
    ParticipantHistory
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def team_id():
    """Generate a test team ID."""
    return uuid4()


@pytest.fixture
def participant_id():
    """Generate a test participant ID."""
    return uuid4()


@pytest.fixture
def base_contract_data(team_id):
    """Generate base contract test data."""
    now = datetime.now()
    return {
        "team_id": team_id,
        "salary": 1000000,
        "length_years": 2,
        "start_date": now,
        "end_date": now + timedelta(days=730)
    }


class TestContractHistory:
    """Test cases for ContractHistory."""
    
    def test_player_contract(self, base_contract_data):
        """Test creating a player contract."""
        contract = ContractHistory(
            **base_contract_data,
            position=Position.CENTER
        )
        assert not contract.is_manager_contract
        assert contract.position == Position.CENTER
        assert contract.manager_role is None
    
    def test_manager_contract(self, base_contract_data):
        """Test creating a manager contract."""
        contract = ContractHistory(
            **base_contract_data,
            manager_role=ManagerRole.GM
        )
        assert contract.is_manager_contract
        assert contract.manager_role == ManagerRole.GM
        assert contract.position is None
    
    def test_contract_active_status(self, base_contract_data):
        """Test contract active status checking."""
        contract = ContractHistory(**base_contract_data, position=Position.CENTER)
        
        # Should be active now
        assert contract.is_active()
        
        # Should be active at start
        assert contract.is_active(base_contract_data["start_date"])
        
        # Should be active at end
        assert contract.is_active(base_contract_data["end_date"])
        
        # Should not be active before start
        assert not contract.is_active(
            base_contract_data["start_date"] - timedelta(days=1)
        )
        
        # Should not be active after end
        assert not contract.is_active(
            base_contract_data["end_date"] + timedelta(days=1)
        )
        
        # Should not be active after early termination
        contract.actual_end_date = datetime.now()
        assert not contract.is_active()


class TestParticipantHistory:
    """Test cases for ParticipantHistory."""
    
    def test_add_player_contract(self, participant_id, team_id):
        """Test adding a player contract."""
        history = ParticipantHistory(participant_id=participant_id)
        
        now = datetime.now()
        history.add_contract(
            team_id=team_id,
            salary=1000000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730),
            position=Position.CENTER
        )
        
        assert len(history.contracts) == 1
        contract = history.contracts[0]
        assert contract.position == Position.CENTER
        assert not contract.is_manager_contract
    
    def test_add_manager_contract(self, participant_id, team_id):
        """Test adding a manager contract."""
        history = ParticipantHistory(participant_id=participant_id)
        
        now = datetime.now()
        history.add_contract(
            team_id=team_id,
            salary=150000,
            length_years=1,
            start_date=now,
            end_date=now + timedelta(days=365),
            manager_role=ManagerRole.GM
        )
        
        assert len(history.contracts) == 1
        contract = history.contracts[0]
        assert contract.manager_role == ManagerRole.GM
        assert contract.is_manager_contract
    
    def test_invalid_contract_no_role(self, participant_id, team_id):
        """Test adding contract without position or role fails."""
        history = ParticipantHistory(participant_id=participant_id)
        
        now = datetime.now()
        with pytest.raises(ValueError, match="Must specify either position or manager_role"):
            history.add_contract(
                team_id=team_id,
                salary=1000000,
                length_years=2,
                start_date=now,
                end_date=now + timedelta(days=730)
            )
    
    def test_current_roles_tracking(self, participant_id, team_id):
        """Test tracking current roles with multiple contracts."""
        history = ParticipantHistory(participant_id=participant_id)
        now = datetime.now()
        
        # Add player contract
        history.add_contract(
            team_id=team_id,
            salary=1000000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730),
            position=Position.CENTER
        )
        
        # Add manager contract
        history.add_contract(
            team_id=team_id,
            salary=150000,
            length_years=1,
            start_date=now,
            end_date=now + timedelta(days=365),
            manager_role=ManagerRole.GM
        )
        
        roles = history.current_roles
        assert roles["player_position"] == Position.CENTER
        assert roles["manager_role"] == ManagerRole.GM
    
    def test_end_specific_contract(self, participant_id, team_id):
        """Test ending specific contract types."""
        history = ParticipantHistory(participant_id=participant_id)
        now = datetime.now()
        
        # Add both contract types
        history.add_contract(
            team_id=team_id,
            salary=1000000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730),
            position=Position.CENTER
        )
        
        history.add_contract(
            team_id=team_id,
            salary=150000,
            length_years=1,
            start_date=now,
            end_date=now + timedelta(days=365),
            manager_role=ManagerRole.GM
        )
        
        # End player contract
        end_date = now + timedelta(days=100)
        history.end_current_contract(
            end_date=end_date,
            reason=TransactionType.RELEASE,
            is_manager_contract=False
        )
        
        # Verify only player contract ended
        roles = history.current_roles
        assert roles["player_position"] is None  # Player contract ended
        assert roles["manager_role"] == ManagerRole.GM  # Manager contract still active
        
        # Verify transaction details
        latest_transaction = history.transactions[-1]
        assert latest_transaction.type == TransactionType.RELEASE
        assert latest_transaction.details["contract_type"] == "player" 