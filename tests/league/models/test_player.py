"""Tests for league player model."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.league.models.player import LeaguePlayer, PlayerContract
from ea_nhl_stats.league.models.player_history import TransactionType


@pytest.fixture
def valid_contract() -> PlayerContract:
    """Create a valid player contract for testing."""
    now = datetime.now()
    return PlayerContract(
        salary=1_000_000,
        length_years=2,
        start_date=now,
        end_date=now + timedelta(days=730)  # 2 years
    )


@pytest.fixture
def valid_player() -> LeaguePlayer:
    """Create a valid player for testing."""
    return LeaguePlayer(
        name="Test Player",
        position=Position.CENTER
    )


@pytest.fixture
def signed_player(valid_player: LeaguePlayer, valid_contract: PlayerContract) -> LeaguePlayer:
    """Create a valid player with contract for testing."""
    return LeaguePlayer(
        player_id=valid_player.player_id,
        name=valid_player.name,
        position=valid_player.position,
        contract=valid_contract
    )


@pytest.fixture
def team_id() -> UUID:
    """Create a team ID for testing."""
    return uuid4()


class TestPlayerContract:
    """Test cases for PlayerContract model."""
    
    def test_valid_contract(self) -> None:
        """Test creation of valid contract."""
        now = datetime.now()
        contract = PlayerContract(
            salary=1_000_000,
            length_years=2,
            start_date=now,
            end_date=now + timedelta(days=730)
        )
        assert contract.salary == 1_000_000
        assert contract.length_years == 2
    
    def test_negative_salary(self) -> None:
        """Test that negative salary raises ValidationError."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            PlayerContract(
                salary=-1_000_000,
                length_years=2,
                start_date=now,
                end_date=now + timedelta(days=730)
            )
    
    def test_zero_length(self) -> None:
        """Test that zero length raises ValidationError."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            PlayerContract(
                salary=1_000_000,
                length_years=0,
                start_date=now,
                end_date=now + timedelta(days=730)
            )
    
    def test_is_active(self, valid_contract: PlayerContract) -> None:
        """Test contract active status checking."""
        now = datetime.now()
        
        # Current
        assert valid_contract.is_active(now)
        
        # Future
        future = now + timedelta(days=1000)
        assert not valid_contract.is_active(future)
        
        # Past
        past = now - timedelta(days=1000)
        assert not valid_contract.is_active(past)


class TestLeaguePlayer:
    """Test cases for LeaguePlayer model."""
    
    def test_valid_player(self, valid_player: LeaguePlayer) -> None:
        """Test creation of valid player."""
        assert valid_player.name == "Test Player"
        assert valid_player.position == Position.CENTER
        assert isinstance(valid_player.player_id, UUID)
    
    def test_player_id_generation(self) -> None:
        """Test that player IDs are unique."""
        player1 = LeaguePlayer(
            name="Player 1",
            position=Position.CENTER
        )
        player2 = LeaguePlayer(
            name="Player 2",
            position=Position.CENTER
        )
        assert player1.player_id != player2.player_id
    
    def test_is_signed(
        self,
        valid_player: LeaguePlayer,
        signed_player: LeaguePlayer
    ) -> None:
        """Test contract status checking."""
        # With contract
        assert signed_player.is_signed
        
        # Without contract
        assert not valid_player.is_signed
    
    def test_is_free_agent(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test free agent status checking."""
        # Without team
        assert valid_player.is_free_agent
        
        # With team
        signed = LeaguePlayer(
            name="Signed Player",
            position=Position.CENTER,
            team_id=team_id
        )
        assert not signed.is_free_agent
    
    def test_sign_with_team(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test signing player to a team."""
        # Sign player
        signed = valid_player.sign_with_team(
            team_id=team_id,
            salary=1_000_000,
            length_years=2
        )
        
        assert signed.team_id == team_id
        assert signed.is_signed
        assert not signed.is_free_agent
        assert len(signed.history.transactions) == 1
        assert signed.history.transactions[0].type == TransactionType.FREE_AGENT_SIGNING
    
    def test_sign_already_signed(
        self,
        signed_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test that signing an already signed player raises error."""
        with pytest.raises(ValueError) as exc_info:
            signed_player.sign_with_team(
                team_id=team_id,
                salary=1_000_000,
                length_years=2
            )
        assert "already has an active contract" in str(exc_info.value)
    
    def test_trade_to_team(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test trading player to a new team."""
        # First sign with initial team
        player = valid_player.sign_with_team(
            team_id=team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Then trade to new team
        new_team_id = uuid4()
        traded = player.trade_to_team(new_team_id)
        
        assert traded.team_id == new_team_id
        assert traded.is_signed  # Contract remains
        assert len(traded.history.transactions) == 2
        assert traded.history.transactions[-1].type == TransactionType.TRADE
    
    def test_trade_free_agent(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test that trading a free agent raises error."""
        with pytest.raises(ValueError) as exc_info:
            valid_player.trade_to_team(team_id)
        assert "Cannot trade a free agent" in str(exc_info.value)
    
    def test_release_from_team(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test releasing player from team."""
        # First sign with team
        player = valid_player.sign_with_team(
            team_id=team_id,
            salary=1_000_000,
            length_years=2
        )
        
        # Then release
        released = player.release_from_team()
        
        assert released.team_id is None
        assert not released.is_signed
        assert released.is_free_agent
        assert len(released.history.transactions) == 2
        assert released.history.transactions[-1].type == TransactionType.RELEASE
    
    def test_release_free_agent(
        self,
        valid_player: LeaguePlayer
    ) -> None:
        """Test that releasing a free agent raises error."""
        with pytest.raises(ValueError) as exc_info:
            valid_player.release_from_team()
        assert "already a free agent" in str(exc_info.value)
    
    def test_expire_contract(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test contract expiration."""
        # First sign with team (contract in past)
        now = datetime.now()
        start = now - timedelta(days=730)  # 2 years ago
        end = now - timedelta(days=1)  # Yesterday
        
        player = LeaguePlayer(
            player_id=valid_player.player_id,
            name=valid_player.name,
            position=valid_player.position,
            contract=PlayerContract(
                salary=1_000_000,
                length_years=2,
                start_date=start,
                end_date=end
            ),
            team_id=team_id
        )
        
        # Expire contract
        expired = player.expire_contract()
        
        assert expired.team_id is None
        assert not expired.is_signed
        assert expired.is_free_agent
        assert len(expired.history.transactions) == 1
        assert expired.history.transactions[0].type == TransactionType.CONTRACT_EXPIRY
    
    def test_expire_active_contract(
        self,
        valid_player: LeaguePlayer,
        team_id: UUID
    ) -> None:
        """Test that expiring an active contract raises error."""
        # First sign with team
        player = valid_player.sign_with_team(
            team_id=team_id,
            salary=1_000_000,
            length_years=2
        )
        
        with pytest.raises(ValueError) as exc_info:
            player.expire_contract()
        assert "Contract has not expired" in str(exc_info.value)
    
    def test_ea_stats_placeholder(self, valid_player: LeaguePlayer) -> None:
        """Test EA stats placeholder method."""
        assert valid_player.get_ea_stats() == [] 