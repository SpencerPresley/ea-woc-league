"""Script to fetch EA API data and save it."""

import json
from ea_nhl_stats.api.get_games_request import GetGamesRequest
from ea_nhl_stats.validators.platform_validator import PlatformValidator
from ea_nhl_stats.validators.match_type_validator import MatchTypeValidator
from ea_nhl_stats.web.web_request import WebRequest


def main():
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
    output_file = "tests/json/ea_response.json"
    with open(output_file, "w") as f:
        json.dump(games, f, indent=2)
    
    print(f"Saved {len(games)} games to {output_file}")


if __name__ == "__main__":
    main() 