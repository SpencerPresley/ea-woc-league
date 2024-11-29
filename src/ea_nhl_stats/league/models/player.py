"""League player model.

This module defines the core player model for the league management system.
Players are distinct from EA NHL player statistics but can be linked to them.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.player import PlayerStats
from ea_nhl_stats.league.models.player_history import (
    PlayerHistory,
    TransactionType
)


class PlayerContract(BaseModel):
    """Player contract details.
    
    Attributes:
        salary: Annual salary amount
        length_years: Contract length in years
        start_date: When the contract begins
        end_date: When the contract expires
    """
    
    salary: int = Field(ge=0, description="Annual salary amount")
    length_years: int = Field(ge=1, description="Contract length in years")
    start_date: datetime = Field(description="Contract start date")
    end_date: datetime = Field(description="Contract end date")
    
    def is_active(self, as_of: Optional[datetime] = None) -> bool:
        """Check if contract is active at a given date.
        
        Args:
            as_of: Date to check, defaults to current date/time
            
        Returns:
            bool: True if contract is active, False otherwise
        """
        check_date = as_of or datetime.now()
        return self.start_date <= check_date <= self.end_date


class LeaguePlayer(BaseModel):
    """Core player model for league management.
    
    This model represents a player in the league system, which is distinct from
    but can be linked to EA NHL player statistics.
    
    Attributes:
        player_id: Unique identifier for the player
        name: Player's display name
        position: Player's primary position
        contract: Player's current contract (if any)
        team_id: ID of player's current team (if any)
        ea_player_id: Link to EA NHL player ID (if any)
        history: Complete player history
    """
    
    player_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the player"
    )
    name: str = Field(description="Player's display name")
    position: Position = Field(description="Player's primary position")
    contract: Optional[PlayerContract] = Field(
        default=None,
        description="Player's current contract"
    )
    team_id: Optional[UUID] = Field(
        default=None,
        description="ID of player's current team"
    )
    ea_player_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL player ID"
    )
    history: PlayerHistory = Field(
        default_factory=lambda: PlayerHistory(player_id=uuid4()),
        description="Complete player history"
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Post initialization hook to set history player_id."""
        if self.history.player_id != self.player_id:
            self.history = PlayerHistory(player_id=self.player_id)
    
    @property
    def is_signed(self) -> bool:
        """Check if player has an active contract.
        
        Returns:
            bool: True if player has an active contract, False otherwise
        """
        return (
            self.contract is not None and
            self.contract.is_active()
        )
    
    @property
    def is_free_agent(self) -> bool:
        """Check if player is a free agent.
        
        Returns:
            bool: True if player has no team, False otherwise
        """
        return self.team_id is None
    
    def sign_with_team(
        self,
        team_id: UUID,
        salary: int,
        length_years: int,
        start_date: Optional[datetime] = None
    ) -> 'LeaguePlayer':
        """Sign player to a new contract with a team.
        
        Args:
            team_id: Team signing the player
            salary: Annual salary amount
            length_years: Contract length in years
            start_date: When the contract begins (defaults to now)
            
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player already has an active contract
        """
        if self.is_signed:
            raise ValueError("Player already has an active contract")
            
        start = start_date or datetime.now()
        end = datetime(
            start.year + length_years,
            start.month,
            start.day,
            start.hour,
            start.minute,
            start.second,
            start.microsecond
        )
        
        contract = PlayerContract(
            salary=salary,
            length_years=length_years,
            start_date=start,
            end_date=end
        )
        
        # Record in history
        self.history.add_contract(
            team_id=team_id,
            salary=salary,
            length_years=length_years,
            start_date=start,
            end_date=end
        )
        self.history.add_transaction(
            TransactionType.FREE_AGENT_SIGNING,
            to_team_id=team_id,
            details={"salary": salary, "length_years": length_years}
        )
        
        # Create new instance with updated state
        return LeaguePlayer(
            player_id=self.player_id,
            name=self.name,
            position=self.position,
            contract=contract,
            team_id=team_id,
            ea_player_id=self.ea_player_id,
            history=self.history
        )
    
    def trade_to_team(self, new_team_id: UUID) -> 'LeaguePlayer':
        """Trade player to a new team.
        
        Args:
            new_team_id: Team receiving the player
            
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player is a free agent
        """
        if self.is_free_agent:
            raise ValueError("Cannot trade a free agent")
            
        old_team_id = self.team_id
        
        # Record in history
        self.history.add_transaction(
            TransactionType.TRADE,
            from_team_id=old_team_id,
            to_team_id=new_team_id
        )
        
        # Create new instance with updated state
        return LeaguePlayer(
            player_id=self.player_id,
            name=self.name,
            position=self.position,
            contract=self.contract,
            team_id=new_team_id,
            ea_player_id=self.ea_player_id,
            history=self.history
        )
    
    def release_from_team(self) -> 'LeaguePlayer':
        """Release player from their current team.
        
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player is already a free agent
        """
        if self.is_free_agent:
            raise ValueError("Player is already a free agent")
            
        old_team_id = self.team_id
        now = datetime.now()
        
        # Record contract end and release in history
        self.history.end_current_contract(
            end_date=now,
            reason=TransactionType.RELEASE
        )
        
        # Create new instance with updated state
        return LeaguePlayer(
            player_id=self.player_id,
            name=self.name,
            position=self.position,
            contract=None,
            team_id=None,
            ea_player_id=self.ea_player_id,
            history=self.history
        )
    
    def expire_contract(self) -> 'LeaguePlayer':
        """Handle contract expiration.
        
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player has no contract or contract isn't expired
        """
        if not self.contract:
            raise ValueError("Player has no contract")
            
        if self.contract.is_active():
            raise ValueError("Contract has not expired")
            
        old_team_id = self.team_id
        
        # Record in history
        self.history.end_current_contract(
            end_date=self.contract.end_date,
            reason=TransactionType.CONTRACT_EXPIRY
        )
        
        # Create new instance with updated state
        return LeaguePlayer(
            player_id=self.player_id,
            name=self.name,
            position=self.position,
            contract=None,
            team_id=None,
            ea_player_id=self.ea_player_id,
            history=self.history
        )
    
    def get_ea_stats(self) -> List[PlayerStats]:
        """Get player's EA NHL statistics.
        
        This is a placeholder method that will be implemented when
        EA stats integration is added.
        
        Returns:
            List[PlayerStats]: List of player's EA NHL statistics
        """
        # TODO: Implement EA stats integration
        return []