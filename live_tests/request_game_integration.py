import json
import logging
from pathlib import Path
from ea_nhl_stats.models.game.club import Match
from pydantic import ValidationError

logging.basicConfig(level=logging.DEBUG, 
                   format="%(asctime)s - %(levelname)s - %(message)s")

def print_match_summary(match: Match) -> None:
    """Print a summary of match data.
    
    Args:
        match: Match object containing game data
    """
    print(f"\nMatch ID: {match.match_id}")
    print(f"Timestamp: {match.timestamp}")
    print(f"Time Ago: {match.time_ago.number} {match.time_ago.unit}")
    
    print("\nClubs:")
    for club_id, club in match.clubs.items():
        print(f"\n  Club {club_id}:")
        if club.details:
            print(f"    Name: {club.details.name}")
            print(f"    Region: {club.details.region_id}")
            print(f"    Team ID: {club.details.team_id}")
        print(f"    Division: {club.club_division}")
        print(f"    Score: {club.score}")
        print(f"    Team Side: {club.team_side}")
        print(f"    Time on Attack: {club.toa}")
        print(f"    Shots: {club.shots}")
        print(f"    Passes: {club.passc}/{club.passa}")

def run_game_info_test(filepath: str = "examples/output/response.json") -> None:
    """Run game info parsing test.
    
    Args:
        filepath: Path to the JSON response file
    """
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
                logging.warning(f"Failed to validate match {match_data.get('matchId', 'unknown')}: {e}")
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