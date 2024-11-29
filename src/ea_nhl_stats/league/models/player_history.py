"""Player history tracking.

This module handles tracking of player history, including past contracts,
teams, and transactions.
"""

from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionType(Enum):
    """Types of player transactions."""
    
    DRAFT = auto()
    FREE_AGENT_SIGNING = auto()
    TRADE = auto()
    RELEASE = auto()
    CONTRACT_EXPIRY = auto()
    RETIREMENT = auto()


class Transaction(BaseModel):
    """Record of a player transaction.
    
    Attributes:
        timestamp: When the transaction occurred
        type: Type of transaction
        from_team_id: Team player came from (if any)
        to_team_id: Team player went to (if any)
        details: Additional transaction details
    """
    
    timestamp: datetime = Field(description="When the transaction occurred")
    type: TransactionType = Field(description="Type of transaction")
    from_team_id: Optional[UUID] = Field(
        default=None,
        description="Team player came from"
    )
    to_team_id: Optional[UUID] = Field(
        default=None,
        description="Team player went to"
    )
    details: Dict = Field(
        default_factory=dict,
        description="Additional transaction details"
    )


class ContractHistory(BaseModel):
    """Historical contract record.
    
    Attributes:
        team_id: Team that signed the contract
        salary: Annual salary amount
        length_years: Contract length in years
        start_date: When the contract began
        end_date: When the contract was set to expire
        actual_end_date: When the contract actually ended (if different)
    """
    
    team_id: UUID = Field(description="Team that signed the contract")
    salary: int = Field(description="Annual salary amount")
    length_years: int = Field(description="Contract length in years")
    start_date: datetime = Field(description="When the contract began")
    end_date: datetime = Field(description="When the contract was set to expire")
    actual_end_date: Optional[datetime] = Field(
        default=None,
        description="When the contract actually ended"
    )


class PlayerHistory(BaseModel):
    """Complete history for a player.
    
    This tracks all historical data for a player, including past contracts,
    teams, and transactions. This data is never cleared and provides a
    complete historical record.
    
    Attributes:
        player_id: The player this history belongs to
        transactions: List of all player transactions
        contracts: List of all player contracts
        teams: List of all teams played for
    """
    
    player_id: UUID = Field(description="The player this history belongs to")
    transactions: List[Transaction] = Field(
        default_factory=list,
        description="List of all player transactions"
    )
    contracts: List[ContractHistory] = Field(
        default_factory=list,
        description="List of all player contracts"
    )
    
    @property
    def current_team_id(self) -> Optional[UUID]:
        """Get the player's current team based on transaction history.
        
        Returns:
            Optional[UUID]: Current team ID, if any
        """
        if not self.transactions:
            return None
            
        latest = sorted(
            self.transactions,
            key=lambda t: t.timestamp,
            reverse=True
        )[0]
        
        return latest.to_team_id
    
    @property
    def teams_played_for(self) -> List[UUID]:
        """Get list of all teams played for.
        
        Returns:
            List[UUID]: List of team IDs
        """
        teams = set()
        for contract in self.contracts:
            teams.add(contract.team_id)
        return sorted(list(teams))
    
    def add_transaction(
        self,
        type: TransactionType,
        *,
        from_team_id: Optional[UUID] = None,
        to_team_id: Optional[UUID] = None,
        details: Optional[Dict] = None
    ) -> None:
        """Add a new transaction to history.
        
        Args:
            type: Type of transaction
            from_team_id: Team player came from (if any)
            to_team_id: Team player went to (if any)
            details: Additional transaction details
        """
        transaction = Transaction(
            timestamp=datetime.now(),
            type=type,
            from_team_id=from_team_id,
            to_team_id=to_team_id,
            details=details or {}
        )
        self.transactions.append(transaction)
    
    def add_contract(
        self,
        team_id: UUID,
        salary: int,
        length_years: int,
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """Add a new contract to history.
        
        Args:
            team_id: Team that signed the contract
            salary: Annual salary amount
            length_years: Contract length in years
            start_date: When the contract begins
            end_date: When the contract expires
        """
        contract = ContractHistory(
            team_id=team_id,
            salary=salary,
            length_years=length_years,
            start_date=start_date,
            end_date=end_date
        )
        self.contracts.append(contract)
    
    def end_current_contract(
        self,
        end_date: datetime,
        reason: TransactionType
    ) -> None:
        """End the current contract early.
        
        Args:
            end_date: When the contract ended
            reason: Why the contract ended
        """
        if self.contracts:
            current = self.contracts[-1]
            current.actual_end_date = end_date
                
        self.add_transaction(
            reason,
            from_team_id=self.current_team_id,
            details={"contract_end_date": end_date.isoformat()}
        ) 