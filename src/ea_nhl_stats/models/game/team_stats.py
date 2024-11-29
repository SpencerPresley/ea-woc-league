"""Team statistics models."""

from typing import List, Optional
from dataclasses import dataclass, field
import warnings
import shortuuid
from plotly.graph_objects import Pie

from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.player_stats import PlayerStatsForSingleGame


@dataclass
class TeamStats:
    """Dataclass representing the statistics of a team for a single game.
    
    Attributes:
        players: List of player stats for the game.
        club_id: The ID of the club.
        goals: The number of goals scored by the team.
        total_shots: The total number of shots taken by the team.
        hits: The number of hits made by the team.
        time_on_attack_seconds: The total time spent on attack in seconds.
        passes_completed: The number of completed passes.
        passes_attempted: The number of attempted passes.
        faceoffs_won: The number of faceoffs won.
        penalty_minutes: The total penalty minutes.
        powerplay_goals: The number of powerplay goals scored.
        powerplay_opportunities: The number of powerplay opportunities.
    """
    
    players: List[PlayerStatsForSingleGame]
    club_id: int
    goals: int
    total_shots: int
    hits: int
    time_on_attack_seconds: int
    passes_completed: int
    passes_attempted: int
    faceoffs_won: int
    penalty_minutes: int
    powerplay_goals: int
    powerplay_opportunities: int
    
    # Calculated fields
    time_on_attack_representation: str = field(init=False)
    passing_percentage: float = field(init=False)
    penalty_minutes_str: str = field(init=False)
    minor_penalties: int = field(init=False)
    major_penalties: int = field(init=False)
    times_penalized: int = field(init=False)
    powerplay_percentage: float = field(init=False)
    powerplay_scored_on_str: str = field(init=False)
    blocked_shots: int = field(init=False)
    short_handed_goals: int = field(init=False)
    short_handed_opportunities: int = field(init=False)
    short_handed_percentage: float = field(init=False)
    
    # Position-specific puck possession
    center_puck_possession_seconds: int = field(init=False)
    left_wing_puck_possession_seconds: int = field(init=False)
    right_wing_puck_possession_seconds: int = field(init=False)
    left_defense_puck_possession_seconds: int = field(init=False)
    right_defense_puck_possession_seconds: int = field(init=False)
    goalie_puck_possession_seconds: int = field(init=False)
    
    # Position-specific puck possession representations
    center_puck_possession_representation: str = field(init=False)
    left_wing_puck_possession_representation: str = field(init=False)
    right_wing_puck_possession_representation: str = field(init=False)
    left_defense_puck_possession_representation: str = field(init=False)
    right_defense_puck_possession_representation: str = field(init=False)
    goalie_puck_possession_representation: str = field(init=False)
    
    # Visualization
    puck_posession_pie_chart: Optional[Pie] = field(init=False)
    
    # Player IDs
    center_player_id: str = field(init=False)
    left_wing_player_id: str = field(init=False)
    right_wing_player_id: str = field(init=False)
    left_defense_player_id: str = field(init=False)
    right_defense_player_id: str = field(init=False)
    goalie_player_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post-initialization method to set various calculated fields."""
        self._set_time_on_attack_representation()
        self._set_pp_percentage()
        self._set_pp_scored_on_str()
        self._set_passing_percentage()
        self._set_penalty_minutes_str()
        self._set_major_minor_penalties()
        self._set_times_penalized()
        self._set_player_ids()
        self._set_blocked_shots()
        self._set_short_handed_goal_stats()
        self._set_puck_possession_stats_reps_chart()

    def _set_time_on_attack_representation(self) -> None:
        """Set the formatted time on attack (MM:SS)."""
        minutes, seconds = divmod(self.time_on_attack_seconds, 60)
        self.time_on_attack_representation = f"{minutes:02d}:{seconds:02d}"

    def _set_pp_percentage(self) -> None:
        """Calculate and set the powerplay percentage."""
        self.powerplay_percentage = (self.powerplay_goals / self.powerplay_opportunities * 100) if self.powerplay_opportunities > 0 else 0

    def _set_pp_scored_on_str(self) -> None:
        """Set the formatted string for powerplay goals/opportunities."""
        self.powerplay_scored_on_str = f"{self.powerplay_goals} / {self.powerplay_opportunities}"

    def _set_passing_percentage(self) -> None:
        """Calculate and set the passing percentage."""
        self.passing_percentage = (self.passes_completed / self.passes_attempted * 100) if self.passes_attempted > 0 else 0

    def _set_penalty_minutes_str(self) -> None:
        """Set the formatted string for penalty minutes."""
        self.penalty_minutes_str = f"{self.penalty_minutes}:00"

    def _set_major_minor_penalties(self) -> None:
        """Set the number of major and minor penalties."""
        self.major_penalties, self.minor_penalties = self._calculate_major_minor_penalties()

    def _calculate_major_minor_penalties(self) -> tuple[int, int]:
        """Calculate major and minor penalties from total penalty minutes.
        
        Returns:
            Tuple containing (major_penalties, minor_penalties)
        """
        n_major_pens = 0
        P = self.penalty_minutes
        
        # Find number of major penalties (5 mins each)
        while (P - (n_major_pens * 5)) % 2 != 0:
            n_major_pens += 1
            
        # Remaining minutes are minor penalties (2 mins each)
        remaining_mins = P - (n_major_pens * 5)
        minor_pens = remaining_mins // 2
        
        return n_major_pens, minor_pens

    def _set_times_penalized(self) -> None:
        """Calculate total number of penalties."""
        self.times_penalized = self.minor_penalties + self.major_penalties

    def _set_blocked_shots(self) -> None:
        """Calculate total blocked shots from player stats."""
        if not self._check_players_instance():
            self.blocked_shots = 0
            return
            
        self.blocked_shots = sum(player.blocked_shots for player in self.players)

    def _set_short_handed_goal_stats(self) -> None:
        """Set short-handed goal statistics."""
        if not self._check_players_instance():
            self.short_handed_goals = 0
            return
            
        self.short_handed_goals = sum(player.short_handed_goals for player in self.players)
        self.short_handed_opportunities = self.times_penalized
        self.short_handed_percentage = (self.short_handed_goals / self.short_handed_opportunities * 100) if self.short_handed_opportunities > 0 else 0

    def _check_players_instance(self) -> bool:
        """Check if all players are valid PlayerStatsForSingleGame instances."""
        valid = all(isinstance(player, PlayerStatsForSingleGame) for player in self.players)
        if not valid:
            warnings.warn("Players are not all instances of PlayerStatsForSingleGame")
        return valid

    def _set_player_ids(self) -> None:
        """Set player IDs for each position."""
        for player in self.players:
            if not hasattr(player, 'playername'):
                continue
                
            player_id = shortuuid.uuid(name=player.playername)
            
            if player.position == Position.CENTER:
                self.center_player_id = player_id
            elif player.position == Position.LEFT_WING:
                self.left_wing_player_id = player_id
            elif player.position == Position.RIGHT_WING:
                self.right_wing_player_id = player_id
            elif player.position == Position.LEFT_DEFENSE:
                self.left_defense_player_id = player_id
            elif player.position == Position.RIGHT_DEFENSE:
                self.right_defense_player_id = player_id
            elif player.position == Position.GOALIE:
                self.goalie_player_id = player_id

    def _set_puck_possession_stats_reps_chart(self) -> None:
        """Set all puck possession related statistics."""
        if not self._check_players_instance():
            self._reset_puck_possession_stats()
            return
            
        self._set_puck_possession_stats()
        self._set_puck_possession_representations()
        self._set_puck_possession_pie_chart()

    def _reset_puck_possession_stats(self) -> None:
        """Reset all puck possession stats to zero."""
        self.center_puck_possession_seconds = 0
        self.left_wing_puck_possession_seconds = 0
        self.right_wing_puck_possession_seconds = 0
        self.left_defense_puck_possession_seconds = 0
        self.right_defense_puck_possession_seconds = 0
        self.goalie_puck_possession_seconds = 0

    def _set_puck_possession_stats(self) -> None:
        """Calculate puck possession times for each position."""
        for player in self.players:
            if not hasattr(player, 'puck_possession_seconds'):
                continue
                
            if player.position == Position.CENTER:
                self.center_puck_possession_seconds = player.puck_possession_seconds
            elif player.position == Position.LEFT_WING:
                self.left_wing_puck_possession_seconds = player.puck_possession_seconds
            elif player.position == Position.RIGHT_WING:
                self.right_wing_puck_possession_seconds = player.puck_possession_seconds
            elif player.position == Position.LEFT_DEFENSE:
                self.left_defense_puck_possession_seconds = player.puck_possession_seconds
            elif player.position == Position.RIGHT_DEFENSE:
                self.right_defense_puck_possession_seconds = player.puck_possession_seconds
            elif player.position == Position.GOALIE:
                self.goalie_puck_possession_seconds = player.puck_possession_seconds

    def _set_puck_possession_representations(self) -> None:
        """Set formatted time representations for all positions."""
        for position in Position:
            if position == Position.NULL:
                continue
                
            seconds = getattr(self, f"{position.name.lower()}_puck_possession_seconds", 0)
            minutes, remaining_seconds = divmod(seconds, 60)
            formatted_time = f"{minutes:02d}:{remaining_seconds:02d}"
            setattr(self, f"{position.name.lower()}_puck_possession_representation", formatted_time)

    def _set_puck_possession_pie_chart(self) -> None:
        """Create a pie chart of puck possession by position."""
        try:
            values = []
            labels = []
            
            for position in Position:
                if position == Position.NULL:
                    continue
                    
                seconds = getattr(self, f"{position.name.lower()}_puck_possession_seconds", 0)
                if seconds > 0:
                    values.append(seconds)
                    labels.append(position.name.replace("_", " ").title())
                    
            if values:
                self.puck_posession_pie_chart = Pie(values=values, labels=labels)
            else:
                self.puck_posession_pie_chart = None
        except Exception as e:
            warnings.warn(f"Failed to create puck possession pie chart: {e}")
            self.puck_posession_pie_chart = None