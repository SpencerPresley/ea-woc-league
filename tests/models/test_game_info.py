"""Tests for game info models."""

from typing import Dict, List, TYPE_CHECKING
import pytest
from ea_nhl_stats.models.game.enums import Position, TeamSide
from ea_nhl_stats.models.game.player_stats import PlayerStats
from ea_nhl_stats.models.game.team_stats import TeamStats
from ea_nhl_stats.models.game.game_result import GameResult

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

def test_player_stats_valid(game_response_data: List[Dict]) -> None:
    """Test PlayerStats model with valid data."""
    first_club_id = next(iter(game_response_data[0]["clubs"]))
    first_player_id = next(iter(game_response_data[0]["players"][first_club_id]))
    player_data = game_response_data[0]["players"][first_club_id][first_player_id]
    
    # Add required fields
    player_data["player_id"] = int(first_player_id)
    player_data["position"] = Position.CENTER  # Default to center for test
    
    stats = PlayerStats.model_validate(player_data)
    assert isinstance(stats.position, Position)
    assert isinstance(stats.goals, int)
    assert isinstance(stats.assists, int)

def test_team_stats_valid(game_response_data: List[Dict]) -> None:
    """Test TeamStats model with valid data."""
    first_club = next(iter(game_response_data[0]["clubs"].values()))
    
    stats = TeamStats(
        club_id=int(first_club["details"]["clubId"]),
        goals=int(first_club["goals"]),
        total_shots=int(first_club["shots"]),
        hits=0,  # Not in JSON
        time_on_attack_seconds=int(first_club["toa"]),
        passes_completed=int(first_club["passc"]),
        passes_attempted=int(first_club["passa"]),
        faceoffs_won=0,  # Not in JSON
        penalty_minutes=0,  # Not in JSON
        powerplay_goals=int(first_club["ppg"]),
        powerplay_opportunities=int(first_club["ppo"]),
        players=[]  # Will be populated elsewhere
    )
    
    assert isinstance(stats.club_id, int)
    assert isinstance(stats.goals, int)
    assert isinstance(stats.total_shots, int)

def test_game_result_valid(game_response_data: List[Dict]) -> None:
    """Test GameResult model with valid data."""
    game_data = game_response_data[0]
    
    # Find home and away teams
    clubs = game_data["clubs"]
    home_club = next(club for club in clubs.values() if club["teamSide"] == "0")
    away_club = next(club for club in clubs.values() if club["teamSide"] == "1")
    
    # Create game result
    result = GameResult(
        game_id=int(game_data["matchId"]),
        timestamp=str(game_data["timestamp"]),
        winner=TeamSide.HOME if home_club["result"] == "1" else TeamSide.AWAY,
        score=f"{home_club['score']}-{away_club['score']}",
        home_team=TeamStats(
            club_id=int(home_club["details"]["clubId"]),
            goals=int(home_club["goals"]),
            total_shots=int(home_club["shots"]),
            hits=0,
            time_on_attack_seconds=int(home_club["toa"]),
            passes_completed=int(home_club["passc"]),
            passes_attempted=int(home_club["passa"]),
            faceoffs_won=0,
            penalty_minutes=0,
            powerplay_goals=int(home_club["ppg"]),
            powerplay_opportunities=int(home_club["ppo"]),
            players=[]
        ),
        away_team=TeamStats(
            club_id=int(away_club["details"]["clubId"]),
            goals=int(away_club["goals"]),
            total_shots=int(away_club["shots"]),
            hits=0,
            time_on_attack_seconds=int(away_club["toa"]),
            passes_completed=int(away_club["passc"]),
            passes_attempted=int(away_club["passa"]),
            faceoffs_won=0,
            penalty_minutes=0,
            powerplay_goals=int(away_club["ppg"]),
            powerplay_opportunities=int(away_club["ppo"]),
            players=[]
        )
    )
    
    assert isinstance(result.game_id, int)
    assert isinstance(result.winner, TeamSide)
    assert isinstance(result.home_team, TeamStats)
    assert isinstance(result.away_team, TeamStats) 