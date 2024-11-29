import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from ea_nhl_stats.models.game.club import Match
from pydantic import ValidationError

logging.basicConfig(level=logging.DEBUG, 
                   format="%(asctime)s - %(levelname)s - %(message)s")

def print_match_summary(match: Match) -> None:
    """Print a summary of match data.
    
    Args:
        match: Match object containing game data
    """
    # Match Overview
    print(f"\n{'='*50}")
    print(f"Match ID: {match.match_id}")
    print(f"Timestamp: {match.timestamp}")
    print(f"Time Ago: {match.time_ago.number} {match.time_ago.unit}")
    
    # Clubs Information
    print(f"\n{'-'*20} CLUBS {'-'*20}")
    for club_id, club in match.clubs.items():
        print(f"\nClub {club_id}:")
        if club.details:
            print(f"  Name: {club.details.name}")
            print(f"  Region: {club.details.region_id}")
            print(f"  Team ID: {club.details.team_id}")
        print(f"  Division: {club.club_division}")
        print(f"  Score: {club.score}")
        print(f"  Team Side: {club.team_side}")
        print(f"  Time on Attack: {club.time_on_attack}")
        print(f"  Shots: {club.shots}")
        print(f"  Passes: {club.passes_completed}/{club.passes_attempted}")
        print(f"  Power Play: {club.powerplay_goals}/{club.powerplay_opportunities}")
        
    # Player Statistics
    print(f"\n{'-'*20} PLAYERS {'-'*20}")
    for club_id, club_players in match.players.items():
        print(f"\nClub {club_id} Players:")
        for player_id, player in club_players.items():
            print(f"\n  Player: {player.player_name}")
            print(f"  Position: {player.position}")
            print(f"  Level: {player.player_level}")
            
            # Skater Stats
            if player.position != "goalie":
                print("  Skater Stats:")
                print(f"    Goals: {player.sk_goals}")
                print(f"    Assists: {player.sk_assists}")
                print(f"    Shots: {player.sk_shots}")
                print(f"    Hits: {player.sk_hits}")
                print(f"    Passes: {player.sk_passes}/{player.sk_pass_attempts}")
                print(f"    +/-: {player.sk_plus_minus}")
            
            # Goalie Stats
            else:
                print("  Goalie Stats:")
                print(f"    Saves: {player.gl_saves}/{player.gl_shots}")
                print(f"    Save %: {player.gl_save_pct:.3f}")
                print(f"    GAA: {player.gl_goals_against_avg:.2f}")
    
    # Aggregate Statistics
    print(f"\n{'-'*20} AGGREGATE STATS {'-'*20}")
    for club_id, agg_stats in match.aggregate.items():
        print(f"\nClub {club_id} Aggregate Stats:")
        print(f"  Team Score: {agg_stats.score}")
        print(f"  Result: {agg_stats.result}")
        print(f"  Total Time on Ice: {agg_stats.toi} seconds")
        if hasattr(agg_stats, 'sk_goals'):
            print(f"  Total Goals: {agg_stats.sk_goals}")
            print(f"  Total Assists: {agg_stats.sk_assists}")
            print(f"  Total Shots: {agg_stats.sk_shots}")
            print(f"  Total Hits: {agg_stats.sk_hits}")
            
            
def run_game_info_test(filepath: str = "examples/output/response.json") -> None:
    """Run game info parsing test."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            logging.error("Expected a list of matches in response")
            return
            
        matches = []
        for match_data in data:
            try:
                match = Match.model_validate(match_data)
                matches.append(match)
            except ValidationError as e:
                logging.warning(
                    f"Failed to validate match {match_data.get('matchId', 'unknown')}: {e}"
                )
                logging.debug(f"Problematic data: {match_data}")  # Added for debugging
                continue
        
        if not matches:
            logging.warning("No valid matches found in response")
            return
            
        for match in matches:
            print_match_summary(match)
            
        logging.info(f"Successfully processed {len(matches)} matches")
        
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in file: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    run_game_info_test()