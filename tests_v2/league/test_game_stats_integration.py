"""Test integration of EA NHL game stats with league player models."""

import json
import pytest
from typing import List, Dict

from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.enums.types import Position
from ea_nhl_stats.league_v2.services.game_stats_service import (
    parse_game_stats,
    update_player_season_stats,
    print_player_game_summary
)

def test_game_stats_integration(capsys):
    """Test parsing game stats and updating player records."""
    
    # Load test data
    with open("tests/json/response.json") as f:
        game_data = json.load(f)
    
    # Create our manager players (one from each team in first game)
    managers = {
        # From team 9688 (CLAMMERS)
        "1003887858515": LeaguePlayer(
            ea_id="1003887858515",
            ea_name="NickSoub",
            discord_id="test_discord_1",
            is_manager=True,
            position=Position.RIGHT_DEFENSE  # We set the position
        ),
        # From team 36218 (JOE NHL)
        "1004141883766": LeaguePlayer(
            ea_id="1004141883766", 
            ea_name="habsy_oiler",
            discord_id="test_discord_2",
            is_manager=True,
            position=Position.CENTER  # We set the position
        )
    }
    
    # Parse matches
    matches = parse_game_stats(game_data)
    assert len(matches) > 0, "Should parse at least one match"
    
    # Test first match
    match = matches[0]
    
    # Process stats for each manager
    for ea_id, manager in managers.items():
        # Find which club this manager was on
        club_id = None
        for cid, club_data in match.players.items():
            if ea_id in club_data:
                club_id = cid
                break
                
        assert club_id is not None, f"Should find club ID for manager {ea_id}"
        
        # Update manager's stats
        update_player_season_stats(manager, match, club_id)
        
        # Print summary
        print_player_game_summary(manager, match, club_id)
        
        # Verify season stats were updated
        assert 2 in manager.season_stats
        season = manager.season_stats[2]
        assert season.games_played == 1
        assert season.goals >= 0
        assert season.assists >= 0
        
        # Position should remain what we set it to
        assert len(season.positions) == 1  # Should only have one position
        assert manager.position in season.positions  # Should be the position we set 