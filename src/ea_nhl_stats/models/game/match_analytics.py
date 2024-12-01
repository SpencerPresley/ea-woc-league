"""
Analytics for EA NHL match data.

This module provides analytics and metrics calculated from match data.
Designed to be extensible for future integration with an analytics repository.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from ea_nhl_stats.models.game.ea_match import Match


@dataclass
class PossessionMetrics:
    """Possession-based metrics for a match."""
    
    possession_differential: float  # Seconds, positive favors home team
    possession_percentage_home: float  # Percentage of total possession
    possession_percentage_away: float
    time_on_attack_differential: float  # Seconds, positive favors home team


@dataclass
class EfficiencyMetrics:
    """Efficiency metrics for both teams."""
    
    home_shooting_efficiency: float  # Goals/Shots %
    away_shooting_efficiency: float
    home_passing_efficiency: float  # Completed/Attempted %
    away_passing_efficiency: float
    home_possession_efficiency: float  # Possession/Attack time %
    away_possession_efficiency: float


@dataclass
class SpecialTeamsMetrics:
    """Special teams metrics for both teams."""
    
    home_powerplay_pct: float
    away_powerplay_pct: float
    home_penalty_kill_pct: float
    away_penalty_kill_pct: float


@dataclass
class MomentumMetrics:
    """Momentum and control metrics."""
    
    home_score: float  # Composite momentum score
    away_score: float
    shot_differential: int  # Positive favors home
    hit_differential: int
    takeaway_differential: int
    scoring_chances_differential: int


class MatchAnalytics:
    """
    Analytics service for a single match.
    
    Calculates various metrics and statistics from match data.
    Designed to be used standalone or as part of a larger analytics system.
    """

    def __init__(self, match: Match):
        """
        Initialize with a match.
        
        Args:
            match: The match to analyze
        """
        self.match = match

    def get_possession_metrics(self) -> Optional[PossessionMetrics]:
        """
        Calculate possession-based metrics.
        
        Returns:
            PossessionMetrics if data available, None if missing required data
        """
        home_agg = self.match.home_aggregate
        away_agg = self.match.away_aggregate
        home_club = self.match.home_club
        away_club = self.match.away_club
        
        if not all([home_agg, away_agg, home_club, away_club]):
            return None
            
        total_possession = float(home_agg.skpossession + away_agg.skpossession)
        
        return PossessionMetrics(
            possession_differential=float(home_agg.skpossession - away_agg.skpossession),
            possession_percentage_home=(float(home_agg.skpossession) / total_possession * 100) if total_possession > 0 else 50.0,
            possession_percentage_away=(float(away_agg.skpossession) / total_possession * 100) if total_possession > 0 else 50.0,
            time_on_attack_differential=float(home_club.time_on_attack) - float(away_club.time_on_attack)
        )

    def get_efficiency_metrics(self) -> Optional[EfficiencyMetrics]:
        """
        Calculate efficiency metrics for both teams.
        
        Returns:
            EfficiencyMetrics if data available, None if missing required data
        """
        home_club = self.match.home_club
        away_club = self.match.away_club
        
        if not home_club or not away_club:
            return None
            
        return EfficiencyMetrics(
            home_shooting_efficiency=(float(home_club.goals) / float(home_club.shots) * 100) 
                if float(home_club.shots) > 0 else 0.0,
            away_shooting_efficiency=(float(away_club.goals) / float(away_club.shots) * 100)
                if float(away_club.shots) > 0 else 0.0,
            home_passing_efficiency=(float(home_club.passes_completed) / float(home_club.passes_attempted) * 100)
                if float(home_club.passes_attempted) > 0 else 0.0,
            away_passing_efficiency=(float(away_club.passes_completed) / float(away_club.passes_attempted) * 100)
                if float(away_club.passes_attempted) > 0 else 0.0,
            home_possession_efficiency=(float(home_club.time_on_attack) / 3600 * 100),  # Convert to percentage of game
            away_possession_efficiency=(float(away_club.time_on_attack) / 3600 * 100)
        )

    def get_special_teams_metrics(self) -> Optional[SpecialTeamsMetrics]:
        """
        Calculate special teams metrics.
        
        Returns:
            SpecialTeamsMetrics if data available, None if missing required data
        """
        home_club = self.match.home_club
        away_club = self.match.away_club
        
        if not home_club or not away_club:
            return None
            
        return SpecialTeamsMetrics(
            home_powerplay_pct=(float(home_club.powerplay_goals) / float(home_club.powerplay_opportunities) * 100)
                if float(home_club.powerplay_opportunities) > 0 else 0.0,
            away_powerplay_pct=(float(away_club.powerplay_goals) / float(away_club.powerplay_opportunities) * 100)
                if float(away_club.powerplay_opportunities) > 0 else 0.0,
            home_penalty_kill_pct=(1 - float(away_club.powerplay_goals) / float(away_club.powerplay_opportunities)) * 100
                if float(away_club.powerplay_opportunities) > 0 else 100.0,
            away_penalty_kill_pct=(1 - float(home_club.powerplay_goals) / float(home_club.powerplay_opportunities)) * 100
                if float(home_club.powerplay_opportunities) > 0 else 100.0
        )

    def get_momentum_metrics(self) -> Optional[MomentumMetrics]:
        """
        Calculate momentum and control metrics.
        
        Returns:
            MomentumMetrics if data available, None if missing required data
        """
        home_agg = self.match.home_aggregate
        away_agg = self.match.away_aggregate
        
        if not home_agg or not away_agg:
            return None
            
        # Weights for momentum calculation
        SHOT_WEIGHT = 1.0
        HIT_WEIGHT = 0.5
        TAKEAWAY_WEIGHT = 0.7
        
        shot_diff = home_agg.skshots - away_agg.skshots
        hit_diff = home_agg.skhits - away_agg.skhits
        takeaway_diff = (home_agg.sktakeaways - home_agg.skgiveaways) - \
                       (away_agg.sktakeaways - away_agg.skgiveaways)
        
        # Calculate momentum score
        momentum_score = (
            shot_diff * SHOT_WEIGHT +
            hit_diff * HIT_WEIGHT +
            takeaway_diff * TAKEAWAY_WEIGHT
        )
        
        return MomentumMetrics(
            home_score=max(0, momentum_score),
            away_score=max(0, -momentum_score),
            shot_differential=shot_diff,
            hit_differential=hit_diff,
            takeaway_differential=takeaway_diff,
            scoring_chances_differential=shot_diff  # Simplified, could be more complex
        )

    def get_all_metrics(self) -> Dict[str, Optional[object]]:
        """
        Get all available metrics in a single call.
        
        Returns:
            Dictionary containing all metrics
        """
        return {
            "possession": self.get_possession_metrics(),
            "efficiency": self.get_efficiency_metrics(),
            "special_teams": self.get_special_teams_metrics(),
            "momentum": self.get_momentum_metrics()
        } 