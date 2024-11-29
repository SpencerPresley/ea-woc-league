"""Live test for stats tracking using real game data."""

import json
from typing import Dict

from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.models.history import SeasonStats
from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.club import Match


def main():
    """Run live test for stats tracking."""
    print("Starting stats tracking test...")
    
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
    print(f"\nProcessing match: {match.match_id}")
    print(f"Teams: {match.clubs.keys()}")
    
    # Track stats for each manager
    for ea_id, manager in managers.items():
        print(f"\n{'='*50}")
        print(f"Processing {manager.name}...")
        
        # Find which club this manager was on
        club_id = None
        for cid, club_data in match.players.items():
            if ea_id in club_data:
                club_id = cid
                break
        
        if not club_id:
            print(f"Manager {manager.name} not found in match")
            continue
            
        print(f"Found on club: {club_id}")
            
        # Get player stats from match
        player_stats = match.players[club_id][ea_id]
        print("\nRaw game stats:")
        print(f"Goals: {player_stats.sk_goals}")
        print(f"Assists: {player_stats.sk_assists}")
        print(f"Shots: {player_stats.sk_shots}")
        print(f"Hits: {player_stats.sk_hits}")
        print(f"Takeaways: {player_stats.sk_takeaways}")
        print(f"Giveaways: {player_stats.sk_giveaways}")
        print(f"Penalty Minutes: {player_stats.sk_penalty_minutes}")
        print(f"Plus/Minus: {player_stats.sk_plus_minus}")
        
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
        
        # Print season stats summary
        print(f"\nSeason 2 Stats for {manager.name} ({manager.position.name}):")
        print(f"Games Played: {stats.games_played}")
        print(f"Goals: {stats.goals}")
        print(f"Assists: {stats.assists}")
        print(f"Points: {stats.points}")
        print(f"Shots: {stats.shots}")
        print(f"Shooting %: {stats.shooting_percentage:.1f}")
        print(f"Hits: {stats.hits}")
        print(f"Takeaways: {stats.takeaways}")
        print(f"Giveaways: {stats.giveaways}")
        print(f"Penalty Minutes: {stats.penalty_minutes}")
        print(f"Plus/Minus: {stats.plus_minus}")
        print(f"Positions: {[pos.name for pos in stats.positions]}")


if __name__ == "__main__":
    main() 