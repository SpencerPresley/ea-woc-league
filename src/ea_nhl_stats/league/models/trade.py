"""Trade models for bulk operations.

This module handles trade operations between teams, including multi-player trades.
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.player_history import TransactionType


class TradeParticipant(BaseModel):
    """A team participating in a trade.
    
    Attributes:
        team_id: The team's ID
        outgoing_players: Players being traded away
        incoming_players: Players being received
    """
    
    team_id: UUID = Field(description="The team's ID")
    outgoing_players: List[LeaguePlayer] = Field(
        default_factory=list,
        description="Players being traded away"
    )
    incoming_players: List[LeaguePlayer] = Field(
        default_factory=list,
        description="Players being received"
    )
    
    def validate_players(self) -> None:
        """Validate that all outgoing players belong to this team.
        
        Raises:
            ValueError: If any player doesn't belong to this team
        """
        for player in self.outgoing_players:
            if player.team_id != self.team_id:
                raise ValueError(
                    f"Player {player.name} does not belong to team {self.team_id}"
                )
            if not player.is_signed:
                raise ValueError(
                    f"Player {player.name} is not under contract"
                )


class TradePackage(BaseModel):
    """A complete trade package between multiple teams.
    
    Attributes:
        participants: Teams involved in the trade
        details: Additional trade details (e.g., conditions)
    """
    
    participants: List[TradeParticipant] = Field(
        min_length=2,
        description="Teams involved in the trade"
    )
    details: Dict = Field(
        default_factory=dict,
        description="Additional trade details"
    )
    
    def validate_trade(self) -> None:
        """Validate the entire trade package.
        
        Checks:
        - Each player appears exactly once
        - Each team's outgoing players belong to them
        - All players are under contract
        
        Raises:
            ValueError: If any validation fails
        """
        # Check for duplicate players
        all_players = []
        for participant in self.participants:
            all_players.extend(participant.outgoing_players)
        
        player_ids = [p.player_id for p in all_players]
        if len(player_ids) != len(set(player_ids)):
            raise ValueError("Duplicate players in trade package")
        
        # Validate each team's players
        for participant in self.participants:
            participant.validate_players()
    
    def execute_trade(self) -> List[LeaguePlayer]:
        """Execute the trade package.
        
        Returns:
            List[LeaguePlayer]: Updated player instances after trade
            
        Raises:
            ValueError: If trade validation fails
        """
        # First validate the trade
        self.validate_trade()
        
        # Map of team_id -> receiving players
        receiving_map = {p.team_id: [] for p in self.participants}
        
        # Build receiving map
        for participant in self.participants:
            for player in participant.outgoing_players:
                # Find receiving team
                for other in self.participants:
                    if other.team_id != participant.team_id:
                        if player in other.incoming_players:
                            receiving_map[other.team_id].append(player)
                            break
        
        # Execute trades
        updated_players = []
        for new_team_id, players in receiving_map.items():
            for player in players:
                updated = player.trade_to_team(new_team_id)
                updated_players.append(updated)
        
        return updated_players


def create_two_team_trade(
    team1_id: UUID,
    team1_players: List[LeaguePlayer],
    team2_id: UUID,
    team2_players: List[LeaguePlayer],
    details: Optional[Dict] = None
) -> TradePackage:
    """Helper function to create a trade between two teams.
    
    Args:
        team1_id: First team's ID
        team1_players: Players from first team
        team2_id: Second team's ID
        team2_players: Players from second team
        details: Additional trade details
        
    Returns:
        TradePackage: The trade package
    """
    return TradePackage(
        participants=[
            TradeParticipant(
                team_id=team1_id,
                outgoing_players=team1_players,
                incoming_players=team2_players
            ),
            TradeParticipant(
                team_id=team2_id,
                outgoing_players=team2_players,
                incoming_players=team1_players
            )
        ],
        details=details or {}
    ) 