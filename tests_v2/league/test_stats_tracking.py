"""Test stats tracking using real game data."""

import json
import pytest
from typing import Dict

from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.models.history import SeasonStats
from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.club import Match


def test_track_manager_stats(capsys):
    """Test tracking manager stats from a real game."""
    
    # Load test data
    with open("tests/json/response.json") as f:
        game_data = json.load(f)
    
    # Create our test managers
    managers: Dict[str, LeaguePlayer] = {
        # Team CLAMMERS (club_id: 9688)
        "1003887858515": LeaguePlayer(
            name="NickSoub",
            position=Position.RIGHT_DEFENSE,
            current_season=2
        ),
        "1004418691339": LeaguePlayer(
            name="Mr Lesp",
            position=Position.CENTER,
            current_season=2
        ),
        
        # Team JOE NHL (club_id: 36218)
        "1004141883766": LeaguePlayer(
            name="habsy_oiler",
            position=Position.LEFT_WING,
            current_season=2
        ),
        "1006828925835": LeaguePlayer(
            name="Mapleleafsfan1_",
            position=Position.LEFT_DEFENSE,
            current_season=2
        )
    }
    
    # Parse first match
    match = Match.model_validate(game_data[0])
    
    # Track stats for each manager
    for ea_id, manager in managers.items():
        # Find which club this manager was on
        club_id = None
        for cid, club_data in match.players.items():
            if ea_id in club_data:
                club_id = cid
                break
        
        if not club_id:
            print(f"Manager {manager.name} not found in match")
            continue
            
        # Get player stats from match
        player_stats = match.players[club_id][ea_id]
        
        # Create/update season stats
        if 2 not in manager.season_stats:  # Season 2
            manager.season_stats[2] = SeasonStats()
        
        stats = manager.season_stats[2]
        stats.games_played += 1
        stats.goals += player_stats.sk_goals
        stats.assists += player_stats.sk_assists
        stats.shots += player_stats.sk_shots
        stats.hits += player_stats.sk_hits
        stats.takeaways += player_stats.sk_takeaways
        stats.giveaways += player_stats.sk_giveaways
        stats.penalty_minutes += player_stats.sk_penalty_minutes
        stats.plus_minus += player_stats.sk_plus_minus
        stats.positions.add(manager.position)  # Use pre-set position
        
        # Print stats summary
        print(f"\nStats for {manager.name} ({manager.position.name}):")
        print(f"Club: {club_id}")
        print(f"Goals: {stats.goals}")
        print(f"Assists: {stats.assists}")
        print(f"Points: {stats.points}")
        print(f"Shots: {stats.shots}")
        print(f"Shooting %: {stats.shooting_percentage:.1f}")
        print(f"Plus/Minus: {stats.plus_minus}")
        
        # Verify stats were tracked
        assert stats.games_played == 1
        assert stats.goals >= 0
        assert stats.assists >= 0
        assert len(stats.positions) == 1
        assert manager.position in stats.positions 