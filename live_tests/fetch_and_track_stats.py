"""Script to fetch EA API data and track player stats."""

import json
from typing import Dict, List

from ea_nhl_stats.api.get_games_request import GetGamesRequest
from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.models.history import SeasonStats
from ea_nhl_stats.models.game.enums import Position
from ea_nhl_stats.models.game.club import Match
from ea_nhl_stats.validators.platform_validator import PlatformValidator
from ea_nhl_stats.validators.match_type_validator import MatchTypeValidator
from ea_nhl_stats.web.web_request import WebRequest


def fetch_and_save_games() -> List[Dict]:
    """Fetch games from EA API and save to file."""
    print("Fetching games from EA API...")
    
    # Create request objects
    web_request = WebRequest()
    platform_validator = PlatformValidator()
    match_type_validator = MatchTypeValidator()
    
    # Create games request
    request = GetGamesRequest(
        club_id=1789,
        platform="common-gen5",
        match_type="club_private",
        web_request=web_request,
        platform_validator=platform_validator,
        match_type_validator=match_type_validator
    )
    
    # Fetch games
    games = request.get_games()
    
    # Save to file
    with open("tests/json/ea_response.json", "w") as f:
        json.dump(games, f, indent=2)
    
    print(f"Saved {len(games)} games to ea_response.json")
    return games


def track_player_stats(games: List[Dict]) -> None:
    """Track player stats from games data."""
    print("\nTracking player stats...")
    
    # Create test managers (we'll pick a few players from the data)
    # We'll update this after looking at the actual data
    managers: Dict[str, LeaguePlayer] = {}
    
    # Process each game
    for game_data in games:
        match = Match.model_validate(game_data)
        print(f"\nProcessing match: {match.match_id}")
        print(f"Teams: {match.clubs.keys()}")
        
        # First game: identify some players to track
        if not managers:
            # Look at first club's players
            first_club_id = list(match.clubs.keys())[0]
            first_club_players = match.players[first_club_id]
            
            # Take first 4 players we find
            for i, (ea_id, player_stats) in enumerate(first_club_players.items()):
                if i >= 4:
                    break
                    
                # Create manager entry
                managers[ea_id] = LeaguePlayer(
                    name=f"Player_{i+1}",  # We'll update with real names if available
                    position=player_stats.position,  # Use their position from first game
                    current_season=2
                )
        
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
            print(f"Position played: {player_stats.position.name}")
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
            stats.positions.add(player_stats.position)  # Track position played in this game
            
            # Print season stats summary
            print(f"\nSeason 2 Stats for {manager.name} (Listed as {manager.position.name}):")
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
            print(f"Positions played: {[pos.name for pos in stats.positions]}")


def main():
    """Main function to run the script."""
    # Fetch and save games
    games = fetch_and_save_games()
    
    # Track stats
    track_player_stats(games)


if __name__ == "__main__":
    main() 