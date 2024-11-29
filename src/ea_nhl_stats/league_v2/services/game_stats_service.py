"""Service for processing EA NHL game stats and integrating with league player models."""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from ea_nhl_stats.models.game.club import Match
from ea_nhl_stats.models.game.player import PlayerStats
from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.models.history import SeasonStats

logging.basicConfig(level=logging.INFO,
                   format="%(asctime)s - %(levelname)s - %(message)s")

def parse_game_stats(json_data: List[Dict]) -> List[Match]:
    """Parse raw game stats JSON into Match objects.
    
    Args:
        json_data: List of match data dictionaries
        
    Returns:
        List of parsed Match objects
    """
    matches = []
    for match_data in json_data:
        try:
            match = Match.model_validate(match_data)
            matches.append(match)
        except Exception as e:
            logging.warning(f"Failed to parse match {match_data.get('matchId', 'unknown')}: {e}")
            continue
    return matches

def extract_player_stats(match: Match, player_id: str, club_id: str) -> Optional[PlayerStats]:
    """Extract stats for a specific player from a match.
    
    Args:
        match: Match object containing all game data
        player_id: EA NHL player ID to extract
        club_id: Club ID the player belongs to
        
    Returns:
        PlayerStats object if found, None otherwise
    """
    try:
        return match.players[club_id][player_id]
    except KeyError:
        return None

def update_player_season_stats(player: LeaguePlayer, match: Match, club_id: str) -> None:
    """Update a player's season stats with data from a match.
    
    Args:
        player: LeaguePlayer object to update
        match: Match containing the player's stats
        club_id: Club ID the player belongs to
    """
    # Get player's stats from the match
    player_stats = extract_player_stats(match, str(player.ea_id), club_id)
    if not player_stats:
        logging.warning(f"No stats found for player {player.ea_id} in match {match.match_id}")
        return

    # Get or create season stats for current season
    current_season = 2  # TODO: Get this from somewhere
    if current_season not in player.season_stats:
        player.season_stats[current_season] = SeasonStats()

    season = player.season_stats[current_season]
    
    # Update season totals
    season.games_played += 1
    season.goals += player_stats.sk_goals
    season.assists += player_stats.sk_assists
    season.shots += player_stats.sk_shots
    season.hits += player_stats.sk_hits
    season.takeaways += player_stats.sk_takeaways
    season.giveaways += player_stats.sk_giveaways
    season.penalty_minutes += player_stats.sk_penalty_minutes
    season.plus_minus += player_stats.sk_plus_minus
    
    # Use the player's pre-set position
    if player.position:
        season.positions.add(player.position)

def print_player_game_summary(player: LeaguePlayer, match: Match, club_id: str) -> None:
    """Print a summary of a player's performance in a game.
    
    Args:
        player: LeaguePlayer object
        match: Match containing the player's stats
        club_id: Club ID the player belongs to
    """
    stats = extract_player_stats(match, str(player.ea_id), club_id)
    if not stats:
        print(f"No stats found for player {player.ea_id}")
        return

    print(f"\nPlayer: {player.ea_name}")
    print(f"Position: {player.position.name if player.position else 'Unknown'}")
    print(f"Goals: {stats.sk_goals}")
    print(f"Assists: {stats.sk_assists}")
    print(f"Shots: {stats.sk_shots}")
    print(f"Hits: {stats.sk_hits}")
    print(f"Takeaways: {stats.sk_takeaways}")
    print(f"Giveaways: {stats.sk_giveaways}")
    print(f"PIM: {stats.sk_penalty_minutes}")
    print(f"+/-: {stats.sk_plus_minus}")
    print(f"TOI: {stats.toi}:00") 