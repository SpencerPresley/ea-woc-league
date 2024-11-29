"""Player and manager models for the league management system.

This module defines the core player and manager models for the EA NHL league system.
It provides classes for tracking player statistics, managing roles, and handling
the relationship between players and managers.
"""

from typing import Optional, Dict, List, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field

from ea_nhl_stats.league_v2.enums.types import Position, ManagerRole
from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats


class SeasonStats(BaseModel):
    """Statistics tracking for a player in a specific season.
    
    This class maintains both game-by-game statistics and season aggregates
    for a player. It serves as a container for all statistical data within
    a single season.
    
    Attributes:
        season: The season number these stats are for
        games_played: Total number of games played
        game_stats: Dictionary of game statistics, keyed by game ID
        positions: Set of positions played during the season
    """
    
    # Season identification
    season: int = Field(
        gt=0,  # Must be positive
        description="Season number these stats are for"
    )
    
    # Game tracking
    games_played: int = Field(
        default=0,
        ge=0,  # Cannot be negative
        description="Number of games played in the season"
    )
    game_stats: Dict[UUID, PlayerStats] = Field(
        default_factory=dict,
        description="Stats for each game, keyed by game ID"
    )
    
    # Position tracking
    positions: Set[Position] = Field(
        default_factory=set,
        description="Positions played during the season"
    )
    
    @computed_field
    @property
    def goals(self) -> int:
        """Total goals scored in the season."""
        return sum(stats.skgoals for stats in self.game_stats.values())
    
    @computed_field
    @property
    def assists(self) -> int:
        """Total assists in the season."""
        return sum(stats.skassists for stats in self.game_stats.values())
    
    @computed_field
    @property
    def points(self) -> int:
        """Total points (goals + assists) in the season."""
        return self.goals + self.assists
    
    @computed_field
    @property
    def shots(self) -> int:
        """Total shots taken in the season."""
        return sum(stats.skshots for stats in self.game_stats.values())
    
    @computed_field
    @property
    def hits(self) -> int:
        """Total hits delivered in the season."""
        return sum(stats.skhits for stats in self.game_stats.values())
    
    @computed_field
    @property
    def takeaways(self) -> int:
        """Total takeaways in the season."""
        return sum(stats.sktakeaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def giveaways(self) -> int:
        """Total giveaways in the season."""
        return sum(stats.skgiveaways for stats in self.game_stats.values())
    
    @computed_field
    @property
    def penalty_minutes(self) -> int:
        """Total penalty minutes in the season."""
        return sum(stats.skpim for stats in self.game_stats.values())
    
    @computed_field
    @property
    def plus_minus(self) -> int:
        """Total plus/minus in the season."""
        return sum(stats.skplusmin for stats in self.game_stats.values())
    
    @computed_field
    @property
    def shooting_percentage(self) -> float:
        """Shooting percentage for the season."""
        if self.shots == 0:
            return 0.0
        return round((self.goals / self.shots) * 100, 2)
    
    @computed_field
    @property
    def points_per_game(self) -> float:
        """Points per game for the season."""
        if self.games_played == 0:
            return 0.0
        return round(self.points / self.games_played, 2)
    
    @computed_field
    @property
    def takeaway_giveaway_ratio(self) -> float:
        """Ratio of takeaways to giveaways."""
        if self.giveaways == 0:
            return 0.0
        return round(self.takeaways / self.giveaways, 2)


class LeaguePlayer(BaseModel):
    """Base player model for all league participants.
    
    This class represents a player in the league system. All participants,
    including managers, are players first. The class provides functionality
    for tracking player statistics, team associations, and EA NHL integration.
    """
    
    # Core player identification
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the player"
    )
    name: str = Field(description="Player's display name")
    position: Position = Field(description="Player's primary position")
    
    # Team association
    team_id: Optional[UUID] = Field(
        default=None,
        description="Current team ID"
    )
    
    # Statistics tracking
    current_season: int = Field(
        gt=0,  # Must be positive
        description="Current season number"
    )
    season_stats: Dict[int, SeasonStats] = Field(
        default_factory=dict,
        description="Stats for each season played"
    )
    
    # EA NHL integration
    ea_id: Optional[str] = Field(
        default=None,
        description="Link to EA NHL player ID"
    )
    ea_name: Optional[str] = Field(
        default=None,
        description="EA NHL display name"
    )
    discord_id: Optional[str] = Field(
        default=None,
        description="Discord user ID"
    )
    
    def add_game_stats(self, match: Match, club_id: str) -> None:
        """Add statistics from a single game.
        
        This method processes match statistics and updates the current season's
        records. If this is the first game of the season, it automatically
        creates the season stats container.
        
        Args:
            match: The completed match
            club_id: The club ID the player was on
            
        Note:
            This method automatically updates all season totals.
        """
        # Get player stats from match
        if not self.ea_id or club_id not in match.players:
            return  # Not our match
            
        player_stats = match.players[club_id].get(self.ea_id)
        if not player_stats:
            return  # Player not in match
        
        # Create season stats if this is first game
        if self.current_season not in self.season_stats:
            self.season_stats[self.current_season] = SeasonStats(
                season=self.current_season
            )
            
        # Add game stats and update season
        season = self.season_stats[self.current_season]
        season.games_played += 1
        
        # Generate UUID from match ID
        hex_str = match.match_id[:32].ljust(32, '0')
        match_uuid = UUID(hex_str)
        
        season.game_stats[match_uuid] = player_stats
        season.positions.add(self.position)  # Use pre-set position


class LeagueManager(LeaguePlayer):
    """A player who also has management responsibilities.
    
    This class extends LeaguePlayer to represent participants who have taken
    on management roles in addition to their player status. It adds tracking
    for management roles and status.
    """
    
    # Management role tracking
    role: ManagerRole = Field(description="Management role within the team")
    is_active_manager: bool = Field(
        default=True,
        description="Whether currently active in management role"
    ) 