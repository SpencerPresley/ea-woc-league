"""Script to track player and team stats from saved EA API data."""

import json
from typing import Dict, List, Set
from uuid import uuid4, UUID
from collections import defaultdict

from ea_nhl_stats.league_v2.models.player import LeaguePlayer
from ea_nhl_stats.league_v2.models.team import LeagueTeam
from ea_nhl_stats.league_v2.enums.types import Position
from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.match_analytics import MatchAnalytics


# Map EA API position strings to our Position enum
POSITION_MAP = {
    "leftWing": Position.LEFT_WING,
    "rightWing": Position.RIGHT_WING,
    "center": Position.CENTER,
    "leftDefense": Position.LEFT_DEFENSE,
    "rightDefense": Position.RIGHT_DEFENSE,
    "defenseMen": Position.LEFT_DEFENSE,  # Default to left defense for generic defense position
    "goalie": Position.GOALIE
}


def load_matches() -> List[Match]:
    """Load and parse matches from saved EA API response."""
    print("Loading matches from saved response...")
    
    with open("live_tests/output/ea_response.json") as f:
        data = json.load(f)
        
    return [Match.model_validate(match_data) for match_data in data]


def create_teams(matches: List[Match]) -> Dict[str, LeagueTeam]:
    """Create teams from match data."""
    print("\nCreating teams...")
    teams: Dict[str, LeagueTeam] = {}
    
    for match in matches:
        for club_id, club in match.clubs.items():
            if club_id not in teams:
                teams[club_id] = LeagueTeam(
                    name=club.details.name,
                    current_season=2,
                    ea_club_id=club_id
                )
                print(f"Created team: {club.details.name} (ID: {club_id})")
    
    return teams


def create_players(matches: List[Match]) -> Dict[str, LeaguePlayer]:
    """Create players from match data."""
    print("\nCreating players...")
    players: Dict[str, LeaguePlayer] = {}
    
    for match in matches:
        for club_id, club_players in match.players.items():
            for player_id, player_data in club_players.items():
                if player_id not in players:
                    # Create player with their first seen position
                    position = POSITION_MAP[player_data.position]
                    players[player_id] = LeaguePlayer(
                        name=player_data.player_name,
                        position=position,
                        current_season=2,
                        ea_id=player_id,
                        ea_name=player_data.player_name
                    )
                    print(f"Created player: {player_data.player_name} ({position.name})")
    
    return players


def track_team_rosters(
    matches: List[Match],
    teams: Dict[str, LeagueTeam],
    players: Dict[str, LeaguePlayer]
) -> Dict[str, Dict[str, List[str]]]:
    """Track team rosters for each match.
    
    Returns:
        Dict mapping team ID to dict of match ID -> list of player IDs
    """
    print("\nTracking team rosters...")
    
    # Track rosters by match: team_id -> {match_id -> [player_ids]}
    rosters: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    
    for match in matches:
        print(f"\nMatch {match.match_id}:")
        for club_id, club_players in match.players.items():
            team = teams[club_id]
            roster = [pid for pid in club_players.keys() if pid in players]
            rosters[club_id][match.match_id] = roster
            
            # Print roster for this match
            print(f"\n{team.name} Roster:")
            for pid in roster:
                player = players[pid]
                print(f"- {player.name} ({player.position.name})")
    
    return rosters


def process_matches(
    matches: List[Match],
    teams: Dict[str, LeagueTeam],
    players: Dict[str, LeaguePlayer],
    rosters: Dict[str, Dict[str, List[str]]]
) -> None:
    """Process matches to update team and player stats."""
    print("\nProcessing matches...")
    
    for match in matches:
        print(f"\nProcessing match: {match.match_id}")
        print(f"Teams: {match.home_club.details.name} vs {match.away_club.details.name}")
        
        # Update team stats and rosters
        for team in teams.values():
            if team.ea_club_id in rosters and match.match_id in rosters[team.ea_club_id]:
                # Clear previous roster
                team.player_ids.clear()
                
                # Add current match roster
                match_roster = rosters[team.ea_club_id][match.match_id]
                for player_id in match_roster:
                    player = players[player_id]
                    team.add_player(player.id)
                    player.team_id = team.id
            
            # Update team stats
            team.add_match(match)
        
        # Update player stats
        for club_id, club_players in match.players.items():
            for player_id, player_stats in club_players.items():
                if player_id in players:  # Skip guests
                    player = players[player_id]
                    player.add_game_stats(match, club_id)


def print_match_analytics(match: Match) -> None:
    """Print analytics for a match."""
    analytics = MatchAnalytics(match)
    
    print(f"\nMatch Analytics:")
    print(f"{'='*80}")
    
    # Possession metrics
    possession = analytics.get_possession_metrics()
    if possession:
        print("\nPossession:")
        print(f"Home: {possession.possession_percentage_home:.1f}%")
        print(f"Away: {possession.possession_percentage_away:.1f}%")
        print(f"Time on Attack Differential: {possession.time_on_attack_differential:+.0f} seconds")
    
    # Efficiency metrics
    efficiency = analytics.get_efficiency_metrics()
    if efficiency:
        print("\nEfficiency:")
        print(f"Shooting %:")
        print(f"  Home: {efficiency.home_shooting_efficiency:.1f}%")
        print(f"  Away: {efficiency.away_shooting_efficiency:.1f}%")
        print(f"Passing %:")
        print(f"  Home: {efficiency.home_passing_efficiency:.1f}%")
        print(f"  Away: {efficiency.away_passing_efficiency:.1f}%")
    
    # Special teams metrics
    special_teams = analytics.get_special_teams_metrics()
    if special_teams:
        print("\nSpecial Teams:")
        print(f"Powerplay %:")
        print(f"  Home: {special_teams.home_powerplay_pct:.1f}%")
        print(f"  Away: {special_teams.away_powerplay_pct:.1f}%")
        print(f"Penalty Kill %:")
        print(f"  Home: {special_teams.home_penalty_kill_pct:.1f}%")
        print(f"  Away: {special_teams.away_penalty_kill_pct:.1f}%")
    
    # Momentum metrics
    momentum = analytics.get_momentum_metrics()
    if momentum:
        print("\nMomentum:")
        print(f"Shot Differential: {momentum.shot_differential:+d}")
        print(f"Hit Differential: {momentum.hit_differential:+d}")
        print(f"Takeaway/Giveaway Differential: {momentum.takeaway_differential:+d}")
        print(f"Momentum Score:")
        print(f"  Home: {momentum.home_score:.1f}")
        print(f"  Away: {momentum.away_score:.1f}")
        print()


def print_team_summary(team: LeagueTeam, players: Dict[str, LeaguePlayer], rosters: Dict[str, Dict[str, List[str]]]) -> None:
    """Print summary of team stats."""
    print(f"\n{'='*80}")
    print(f"Team Summary: {team.name}")
    print(f"{'='*80}")
    
    if team.current_season not in team.season_stats:
        print("No stats available")
        return
    
    stats = team.season_stats[team.current_season]
    
    # Print roster history
    if team.ea_club_id in rosters:
        print("\nRoster History:")
        for match_id, roster in rosters[team.ea_club_id].items():
            print(f"\nMatch {match_id}:")
            
            # Group players by position
            by_position = defaultdict(list)
            for pid in roster:
                player = players[pid]
                by_position[player.position].append(player.name)
            
            # Print by position
            for pos in Position:
                if pos in by_position:
                    print(f"{pos.name}:")
                    for name in by_position[pos]:
                        print(f"  - {name}")
    
    print("\nSeason Record:")
    print(f"Games Played: {stats.matches_played}")
    print(f"Wins: {stats.wins}")
    print(f"Losses: {stats.losses}")
    print(f"Points: {stats.points}")
    print(f"Win %: {stats.win_percentage:.1f}%")
    
    print("\nOffense:")
    print(f"Goals For: {stats.goals_for} ({stats.goals_per_game:.1f}/game)")
    print(f"Shots: {stats.shots}")
    print(f"Shooting %: {stats.shooting_percentage:.1f}%")
    print(f"Time on Attack: {stats.time_on_attack} seconds ({stats.time_on_attack_per_game:.1f}/game)")
    
    print("\nDefense:")
    print(f"Goals Against: {stats.goals_against} ({stats.goals_against_per_game:.1f}/game)")
    print(f"Goal Differential: {stats.goal_differential}")
    
    print("\nSpecial Teams:")
    print(f"Powerplay: {stats.powerplay_goals}/{stats.powerplay_opportunities} ({stats.powerplay_percentage:.1f}%)")
    if stats.penalty_kill_opportunities > 0:
        print(f"Penalty Kill: {stats.penalty_kill_goals_against}/{stats.penalty_kill_opportunities} ({stats.penalty_kill_percentage:.1f}%)")


def print_player_summary(player: LeaguePlayer, teams: Dict[str, LeagueTeam], rosters: Dict[str, Dict[str, List[str]]]) -> None:
    """Print summary of player stats."""
    print(f"\n{'='*80}")
    print(f"Player Summary: {player.name}")
    print(f"{'='*80}")
    
    # Print team history
    print("\nTeam History:")
    for team_id, team_rosters in rosters.items():
        team = teams[team_id]
        matches_with_team = [
            match_id for match_id, roster in team_rosters.items()
            if player.ea_id in roster
        ]
        if matches_with_team:
            print(f"{team.name}: {len(matches_with_team)} games")
            print("Matches:", ", ".join(matches_with_team))
    
    print(f"\nOfficial Position: {player.position.name}")
    
    if player.current_season not in player.season_stats:
        print("No stats available")
        return
    
    stats = player.season_stats[player.current_season]
    
    print("\nGames:")
    print(f"Games Played: {stats.games_played}")
    print(f"Positions: {[pos.name for pos in stats.positions]}")
    
    print("\nScoring:")
    print(f"Goals: {stats.goals}")
    print(f"Assists: {stats.assists}")
    print(f"Points: {stats.points} ({stats.points_per_game:.2f}/game)")
    print(f"Shots: {stats.shots}")
    print(f"Shooting %: {stats.shooting_percentage:.1f}%")
    
    print("\nPhysical:")
    print(f"Hits: {stats.hits}")
    print(f"Takeaways: {stats.takeaways}")
    print(f"Giveaways: {stats.giveaways}")
    if stats.giveaways > 0:
        print(f"Takeaway/Giveaway: {stats.takeaway_giveaway_ratio:.2f}")
    
    print("\nOther:")
    print(f"Penalty Minutes: {stats.penalty_minutes}")
    print(f"Plus/Minus: {stats.plus_minus}")


def main():
    """Main function to run the script."""
    # Load and parse matches
    matches = load_matches()
    
    # Create teams and players
    teams = create_teams(matches)
    players = create_players(matches)
    
    # Track team rosters for each match
    rosters = track_team_rosters(matches, teams, players)
    
    # Process all matches
    process_matches(matches, teams, players, rosters)
    
    # Print match analytics
    print("\nMatch Analytics:")
    for match in matches:
        print(f"\nMatch {match.match_id}: {match.home_club.details.name} vs {match.away_club.details.name}")
        print_match_analytics(match)
    
    # Print team summaries
    print("\nTeam Summaries:")
    for team in teams.values():
        print_team_summary(team, players, rosters)
    
    # Print player summaries
    print("\nPlayer Summaries:")
    for player in players.values():
        print_player_summary(player, teams, rosters)


if __name__ == "__main__":
    main() 