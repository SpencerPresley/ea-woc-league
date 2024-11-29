"""Team model for league management.

This module defines the core team model and its capabilities for roster
and trade management.
"""

from datetime import datetime
from typing import List, Dict, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.league.enums.league_types import LeagueTier
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.trade import TradeParticipant


class TeamRoster(BaseModel):
    """Team roster management.
    
    Attributes:
        active_players: Currently active players
        inactive_players: Players on IR, suspended, etc.
    """
    
    active_players: List[LeaguePlayer] = Field(
        default_factory=list,
        description="Currently active players"
    )
    inactive_players: List[LeaguePlayer] = Field(
        default_factory=list,
        description="Players on IR, suspended, etc."
    )
    
    @property
    def all_players(self) -> List[LeaguePlayer]:
        """Get all players on the roster.
        
        Returns:
            List[LeaguePlayer]: All players, active and inactive
        """
        return self.active_players + self.inactive_players
    
    @property
    def total_salary(self) -> int:
        """Calculate total salary for all players.
        
        Returns:
            int: Total salary amount
        """
        return sum(
            p.contract.salary for p in self.all_players
            if p.contract is not None
        )
    
    def add_player(self, player: LeaguePlayer, active: bool = True) -> None:
        """Add a player to the roster.
        
        Args:
            player: Player to add
            active: Whether to add as active (True) or inactive (False)
            
        Raises:
            ValueError: If player already on roster
        """
        if player in self.all_players:
            raise ValueError(f"Player {player.name} already on roster")
            
        if active:
            self.active_players.append(player)
        else:
            self.inactive_players.append(player)
    
    def remove_player(self, player: LeaguePlayer) -> None:
        """Remove a player from the roster.
        
        Args:
            player: Player to remove
            
        Raises:
            ValueError: If player not on roster
        """
        if player in self.active_players:
            self.active_players.remove(player)
        elif player in self.inactive_players:
            self.inactive_players.remove(player)
        else:
            raise ValueError(f"Player {player.name} not on roster")
    
    def set_player_status(self, player: LeaguePlayer, active: bool) -> None:
        """Change a player's active/inactive status.
        
        Args:
            player: Player to update
            active: New status (True for active, False for inactive)
            
        Raises:
            ValueError: If player not on roster
        """
        try:
            self.remove_player(player)
            self.add_player(player, active)
        except ValueError as e:
            raise ValueError(f"Player {player.name} not on roster") from e


class LeagueTeam(BaseModel):
    """Core team model for league management.
    
    Attributes:
        team_id: Unique identifier for the team
        name: Team's display name
        tier: Team's league tier
        roster: Team's player roster
        ea_team_id: Link to EA NHL team ID (if any)
    """
    
    team_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the team"
    )
    name: str = Field(description="Team's display name")
    tier: LeagueTier = Field(description="Team's league tier")
    roster: TeamRoster = Field(
        default_factory=TeamRoster,
        description="Team's player roster"
    )
    ea_team_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL team ID"
    )
    
    def sign_player(self, player: LeaguePlayer) -> LeaguePlayer:
        """Add a signed player to the roster.
        
        Args:
            player: Player to add
            
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player already on roster or signed to wrong team
        """
        if player.team_id != self.team_id:
            raise ValueError(
                f"Player {player.name} not signed to team {self.name}"
            )
        
        self.roster.add_player(player)
        return player
    
    def release_player(self, player: LeaguePlayer) -> LeaguePlayer:
        """Release a player from the roster.
        
        Args:
            player: Player to release
            
        Returns:
            LeaguePlayer: Updated player instance
            
        Raises:
            ValueError: If player not on roster
        """
        self.roster.remove_player(player)
        return player.release_from_team()
    
    def propose_trade(
        self,
        other_team: 'LeagueTeam',
        outgoing_players: List[LeaguePlayer],
        incoming_players: List[LeaguePlayer],
        details: Optional[Dict] = None
    ) -> TradeParticipant:
        """Create a trade proposal with another team.
        
        Args:
            other_team: Team to trade with
            outgoing_players: Players to trade away
            incoming_players: Players to receive
            details: Additional trade details
            
        Returns:
            TradeParticipant: This team's trade participation
            
        Raises:
            ValueError: If any players not on correct rosters
        """
        # Verify outgoing players are on our roster
        for player in outgoing_players:
            if player not in self.roster.all_players:
                raise ValueError(
                    f"Player {player.name} not on {self.name}'s roster"
                )
        
        # Verify incoming players are on other team's roster
        for player in incoming_players:
            if player not in other_team.roster.all_players:
                raise ValueError(
                    f"Player {player.name} not on {other_team.name}'s roster"
                )
        
        return TradeParticipant(
            team_id=self.team_id,
            outgoing_players=outgoing_players,
            incoming_players=incoming_players
        ) 