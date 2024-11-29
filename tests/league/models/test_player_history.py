"""Tests for player history tracking."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.league.models.player_history import (
    PlayerHistory,
    Transaction,
    TransactionType,
    ContractHistory
)

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture


@pytest.fixture
def player_id() -> UUID:
    """Create a player ID for testing."""
    return uuid4()


@pytest.fixture
def team_id() -> UUID:
    """Create a team ID for testing."""
    return uuid4()


@pytest.fixture
def history(player_id: UUID) -> PlayerHistory:
    """Create a player history for testing."""
    return PlayerHistory(player_id=player_id)


class TestTransaction:
    """Test cases for Transaction model."""
    
    def test_valid_transaction(self, team_id: UUID) -> None:
        """Test creation of valid transaction."""
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.FREE_AGENT_SIGNING,
            to_team_id=team_id,
            details={"salary": 1_000_000}
        )
        assert transaction.type == TransactionType.FREE_AGENT_SIGNING
        assert transaction.to_team_id == team_id
        assert transaction.details["salary"] == 1_000_000
    
    def test_trade_transaction(self, team_id: UUID) -> None:
        """Test creation of trade transaction."""
        new_team_id = uuid4()
        transaction = Transaction(
            timestamp=datetime.now(),
            type=TransactionType.TRADE,
            from_team_id=team_id,
            to_team_id=new_team_id
        )
        assert transaction.from_team_id == team_id
        assert transaction.to_team_id == new_team_id


class TestContractHistory:
    """Test cases for ContractHistory model."""
    
    def test_valid_contract(self, team_id: UUID) -> None:
        """Test creation of valid contract history."""
        now = datetime.now()
        contract = ContractHistory(
            team_id=team_id,
            salary=1_000_000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730)
        )
        assert contract.team_id == team_id
        assert contract.salary == 1_000_000
        assert contract.length_years == 2
        assert contract.actual_end_date is None
    
    def test_early_termination(self, team_id: UUID) -> None:
        """Test early contract termination."""
        now = datetime.now()
        contract = ContractHistory(
            team_id=team_id,
            salary=1_000_000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730),
            actual_end_date=now + timedelta(days=365)
        )
        assert contract.actual_end_date is not None


class TestPlayerHistory:
    """Test cases for PlayerHistory model."""
    
    def test_empty_history(self, history: PlayerHistory) -> None:
        """Test newly created history."""
        assert not history.transactions
        assert not history.contracts
        assert history.current_team_id is None
        assert not history.teams_played_for
    
    def test_add_transaction(
        self,
        history: PlayerHistory,
        team_id: UUID
    ) -> None:
        """Test adding transaction to history."""
        history.add_transaction(
            TransactionType.FREE_AGENT_SIGNING,
            to_team_id=team_id,
            details={"salary": 1_000_000}
        )
        
        assert len(history.transactions) == 1
        assert history.current_team_id == team_id
    
    def test_add_contract(
        self,
        history: PlayerHistory,
        team_id: UUID
    ) -> None:
        """Test adding contract to history."""
        now = datetime.now()
        history.add_contract(
            team_id=team_id,
            salary=1_000_000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730)
        )
        
        assert len(history.contracts) == 1
        assert team_id in history.teams_played_for
    
    def test_end_current_contract(
        self,
        history: PlayerHistory,
        team_id: UUID
    ) -> None:
        """Test ending current contract."""
        # Add contract
        now = datetime.now()
        history.add_contract(
            team_id=team_id,
            salary=1_000_000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730)
        )
        
        # End contract
        end_date = now + timedelta(days=365)
        history.end_current_contract(
            end_date=end_date,
            reason=TransactionType.RELEASE
        )
        
        assert len(history.transactions) == 1
        assert history.transactions[0].type == TransactionType.RELEASE
        assert history.contracts[0].actual_end_date == end_date 