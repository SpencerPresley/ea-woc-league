"""Script to analyze season data structure with real match data.

This script:
1. Creates a new season using the builder
2. Loads a match from EA API data
3. Updates the season's teams and players with the match data
4. Outputs the complete data structure
"""

import json
from typing import Dict, TextIO
from uuid import UUID

from pydantic import BaseModel

from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.match_analytics import MatchAnalytics
from ea_nhl_stats.league.models.season import Season, SeasonBuilder, LeagueData
from ea_nhl_stats.league.enums.league_level import LeagueLevel
from ea_nhl_stats.league.enums.team_identifier import TeamIdentifier
from ea_nhl_stats.league.models.teams.base_team import LeagueTeam
from ea_nhl_stats.league.models.players.league_player import LeaguePlayer, ManagerInfo
from ea_nhl_stats.league.enums.types import Position, ManagerRole


# Mapping of EA club names to our TeamIdentifiers
# This would be provided/maintained by managers
CLUB_NAME_MAP = {
    "LG Blues": TeamIdentifier.ST_LOUIS_BLUES,
    "LG Calgary Flames": TeamIdentifier.CALGARY_FLAMES
}

# Map EA API position strings to our Position enum (from track_stats.py)
POSITION_MAP = {
    "leftWing": Position.LEFT_WING,
    "rightWing": Position.RIGHT_WING,
    "center": Position.CENTER,
    "leftDefense": Position.LEFT_DEFENSE,
    "rightDefense": Position.RIGHT_DEFENSE,
    "defenseMen": Position.LEFT_DEFENSE,  # Default to left defense for generic defense position
    "goalie": Position.GOALIE
}

# For testing - assign some managers
# In reality this would come from a database or config
MANAGER_MAP = {
    # Blues managers
    "1669236396": ManagerRole.GM,  # vViperrz
    "1719294631": ManagerRole.AGM,  # Pxtlick
    # Flames managers
    "1847429195": ManagerRole.GM,  # Pertuu-
    "1963192309": ManagerRole.AGM,  # Zapssey
}


class DataStructureAnalysis(BaseModel):
    """Complete picture of our data model relationships."""
    
    # Raw EA data
    raw_match: Dict
    
    # Processed EA models
    match: Match
    
    # League data
    league: LeagueData


def create_season() -> Season:
    """Create a new season with NHL teams."""
    return (SeasonBuilder()
        .with_season_id("2024")
        .with_tier(LeagueLevel.NHL)
        .build()
    )


def process_match_data(season: Season, match: Match) -> None:
    """Process match data into the season structure.
    
    Args:
        season: The season to update
        match: The match data to process
    """
    nhl_tier = season.tiers[LeagueLevel.NHL]
    
    # Process each club's data
    for club_id, club in match.clubs.items():
        # Get team ID from club name mapping
        team_id = CLUB_NAME_MAP.get(club.details.name)
        if not team_id:
            print(f"Warning: No team mapping found for club {club.details.name}")
            continue
            
        team = nhl_tier.teams[team_id]
        
        # Update team's EA info if not set
        if not team.ea_club_id:
            team.ea_club_id = club_id
            team.ea_club_name = club.details.name
        
        # Process players
        if club_id in match.players:
            for player_id, player_stats in match.players[club_id].items():
                # Create player if not exists
                if player_id not in nhl_tier.players:
                    position = POSITION_MAP.get(player_stats.position, Position.CENTER)
                    
                    player = LeaguePlayer(
                        name=player_stats.player_name,
                        position=position,
                        ea_id=player_id,
                        ea_name=player_stats.player_name
                    )
                    
                    # Check if player is a manager
                    if player_id in MANAGER_MAP:
                        player.manager_info = ManagerInfo(
                            role=MANAGER_MAP[player_id],
                            is_active=True
                        )
                    
                    nhl_tier.players[player_id] = player
                
                player = nhl_tier.players[player_id]
                
                # Only add to roster and update stats if this is their team
                if club_id == team.ea_club_id:
                    # Add player to roster
                    team.add_roster_player(player)
                    player.join_team(team.id)
                    
                    # If player is a manager, add to team management
                    if player.manager_info:
                        team.add_manager(player, player.manager_info.role)
                    
                    # Update stats
                    player.add_game_stats(team.id, match.match_id, player_stats)
        
        # Update team stats
        team.stats.add_match(match.match_id, club)


def write_human_readable_summary(season: Season, match: Match, file: TextIO) -> None:
    """Write human-readable summary to both console and file.
    
    Args:
        season: The season to summarize
        match: The match being analyzed
        file: File to write to
    """
    def write(text: str) -> None:
        """Write text to both console and file."""
        print(text)
        file.write(text + "\n")
    
    write("\nSeason Structure Summary:")
    write("=" * 80)
    
    nhl_tier = season.tiers[LeagueLevel.NHL]
    
    write(f"\nSeason ID: {season.season_id}")
    write(f"Number of Tiers: {len(season.tiers)}")
    
    # Match analytics
    analytics = MatchAnalytics(match)
    write("\nMatch Analytics:")
    write("-" * 40)
    
    possession = analytics.get_possession_metrics()
    if possession:
        write("\nPossession:")
        write(f"Home: {possession.possession_percentage_home:.1f}%")
        write(f"Away: {possession.possession_percentage_away:.1f}%")
        write(f"Time on Attack Differential: {possession.time_on_attack_differential:+.0f} seconds")
    
    efficiency = analytics.get_efficiency_metrics()
    if efficiency:
        write("\nEfficiency:")
        write(f"Shooting %:")
        write(f"  Home: {efficiency.home_shooting_efficiency:.1f}%")
        write(f"  Away: {efficiency.away_shooting_efficiency:.1f}%")
        write(f"Passing %:")
        write(f"  Home: {efficiency.home_passing_efficiency:.1f}%")
        write(f"  Away: {efficiency.away_passing_efficiency:.1f}%")
    
    momentum = analytics.get_momentum_metrics()
    if momentum:
        write("\nMomentum:")
        write(f"Shot Differential: {momentum.shot_differential:+d}")
        write(f"Hit Differential: {momentum.hit_differential:+d}")
        write(f"Takeaway/Giveaway Differential: {momentum.takeaway_differential:+d}")
    
    # Team summaries
    write("\nNHL Teams:")
    write("-" * 40)
    for team_id, team in nhl_tier.teams.items():
        write(f"\n- {team.official_name}")
        write(f"  ID: {team.id}")
        write(f"  League Level: {team.league_level.value}")
        write(f"  EA Club ID: {team.ea_club_id}")
        write(f"  EA Club Name: {team.ea_club_name}")
        write(f"  Current roster: {len(team.current_roster)}")
        write(f"  Historical players: {len(team.historical_players)}")
        write(f"  Managers: {len(team.management)}")
        
        # Team stats
        if team.stats.matches:
            write("\n  Team Stats:")
            write(f"    Matches Played: {team.stats.matches_played}")
            write(f"    Wins: {team.stats.wins}")
            write(f"    Losses: {team.stats.losses}")
            write(f"    Points: {team.stats.points}")
            write(f"    Win %: {team.stats.win_percentage:.1f}%")
            write(f"    Goals For: {team.stats.goals_for}")
            write(f"    Goals Against: {team.stats.goals_against}")
            write(f"    Goals/Game: {team.stats.goals_per_game:.1f}")
            write(f"    Goals Against/Game: {team.stats.goals_against_per_game:.1f}")
            write(f"    Goal Differential: {team.stats.goal_differential:+d}")
            write(f"    Shots: {team.stats.shots}")
            write(f"    Shots Against: {team.stats.shots_against}")
            write(f"    Shooting %: {team.stats.shooting_percentage:.1f}%")
            write(f"    Powerplay Goals: {team.stats.powerplay_goals}")
            write(f"    Powerplay Opportunities: {team.stats.powerplay_opportunities}")
            write(f"    Powerplay %: {team.stats.powerplay_percentage:.1f}%")
            write(f"    PK Goals Against: {team.stats.penalty_kill_goals_against}")
            write(f"    PK Opportunities: {team.stats.penalty_kill_opportunities}")
            write(f"    PK %: {team.stats.penalty_kill_percentage:.1f}%")
            write(f"    Time on Attack: {team.stats.time_on_attack} seconds")
            write(f"    Time on Attack/Game: {team.stats.time_on_attack_per_game:.1f} seconds")
        
        # Current roster with stats
        write("\n  Current Roster:")
        for player_id in team.current_roster:
            player = team.current_roster[player_id]
            write(f"\n    - {player.name} ({player.position.name})")
            if player.manager_info:
                write(f"      Role: {player.manager_info.role.value}")
            write(f"      EA ID: {player.ea_id}")
            write(f"      EA Name: {player.ea_name}")
            write(f"      Current Team: {player.current_team}")
            write(f"      Teams Played For: {len(player.team_stats)}")
            
            # Get latest stats for this player
            player_stats = player.team_stats[team.id]
            latest_match_id = list(player_stats.game_stats.keys())[-1]
            latest_stats = player_stats.game_stats[latest_match_id]
            
            # Basic info
            write("\n      Basic Info:")
            write(f"        Level: {latest_stats.player_level}")
            write(f"        Level Display: {latest_stats.player_level_display}")
            write(f"        Position: {latest_stats.position}")
            write(f"        Position Sorted: {latest_stats.pos_sorted}")
            write(f"        Platform: {latest_stats.client_platform}")
            write(f"        Is Guest: {latest_stats.is_guest}")
            write(f"        DNF: {latest_stats.player_dnf}")
            write(f"        Game Type: {latest_stats.pnhl_online_game_type}")
            
            # Team info
            write("\n      Team Info:")
            write(f"        Team ID: {latest_stats.team_id}")
            write(f"        Team Side: {latest_stats.team_side}")
            write(f"        Score: {latest_stats.score}")
            write(f"        Opponent Team ID: {latest_stats.opponent_team_id}")
            write(f"        Opponent Club ID: {latest_stats.opponent_club_id}")
            write(f"        Opponent Score: {latest_stats.opponent_score}")
            
            # Player ratings
            write("\n      Ratings:")
            write(f"        Offense: {latest_stats.rating_offense:.1f}")
            write(f"        Defense: {latest_stats.rating_defense:.1f}")
            write(f"        Teamplay: {latest_stats.rating_teamplay:.1f}")
            
            # Time stats
            write("\n      Time Stats:")
            write(f"        Time on Ice: {latest_stats.toi} minutes")
            write(f"        Time on Ice: {latest_stats.toi_seconds} seconds")
            write(f"        Possession Time: {latest_stats.skpossession} seconds")
            
            # Skater stats
            write("\n      Skater Stats:")
            write(f"        Goals: {latest_stats.skgoals}")
            write(f"        Assists: {latest_stats.skassists}")
            write(f"        Points: {latest_stats.points}")
            write(f"        Plus/Minus: {latest_stats.skplusmin:+d}")
            write(f"        PIM: {latest_stats.skpim}")
            write(f"        Penalties Drawn: {latest_stats.skpenaltiesdrawn}")
            
            # Shooting
            write("\n      Shooting:")
            write(f"        Shot Attempts: {latest_stats.skshotattempts}")
            write(f"        Shots on Goal: {latest_stats.skshots}")
            write(f"        Shot on Net %: {latest_stats.skshotonnetpct:.1f}%")
            write(f"        Shooting %: {latest_stats.skshotpct:.1f}%")
            write(f"        Missed Shots: {latest_stats.shots_missed}")
            
            # Passing
            write("\n      Passing:")
            write(f"        Pass Attempts: {latest_stats.skpassattempts}")
            write(f"        Completed Passes: {latest_stats.skpasses}")
            write(f"        Pass %: {latest_stats.skpasspct:.1f}%")
            write(f"        Missed Passes: {latest_stats.passes_missed}")
            write(f"        Saucer Passes: {latest_stats.sksaucerpasses}")
            
            # Physical play
            write("\n      Physical Play:")
            write(f"        Hits: {latest_stats.skhits}")
            write(f"        Blocked Shots: {latest_stats.skbs}")
            write(f"        Deflections: {latest_stats.skdeflections}")
            write(f"        Interceptions: {latest_stats.skinterceptions}")
            
            # Puck control
            write("\n      Puck Control:")
            write(f"        Takeaways: {latest_stats.sktakeaways}")
            write(f"        Giveaways: {latest_stats.skgiveaways}")
            
            # Faceoffs
            write("\n      Faceoffs:")
            write(f"        Faceoffs Won: {latest_stats.skfow}")
            write(f"        Faceoffs Lost: {latest_stats.skfol}")
            write(f"        Total Faceoffs: {latest_stats.faceoffs_total}")
            write(f"        Faceoff %: {latest_stats.skfopct:.1f}%")
            
            # Special teams
            write("\n      Special Teams:")
            write(f"        Powerplay Goals: {latest_stats.skppg}")
            write(f"        Shorthanded Goals: {latest_stats.skshg}")
            write(f"        Game Winning Goals: {latest_stats.skgwg}")
            write(f"        PK Clear Zone: {latest_stats.skpkclearzone}")
            
            # Penalties
            write("\n      Penalties:")
            write(f"        Total PIM: {latest_stats.skpim}")
            write(f"        Major Penalties: {latest_stats.major_penalties}")
            write(f"        Minor Penalties: {latest_stats.minor_penalties}")
            write(f"        Total Penalties: {latest_stats.total_penalties}")
            write(f"        Penalties Drawn: {latest_stats.skpenaltiesdrawn}")
            
            # Goalie stats (if applicable)
            if player.position == Position.GOALIE:
                write("\n      Goalie Stats:")
                write(f"        Goals Against: {latest_stats.glga}")
                write(f"        GAA: {latest_stats.glgaa:.2f}")
                write(f"        Saves: {latest_stats.glsaves}")
                write(f"        Shots Against: {latest_stats.glshots}")
                write(f"        Save %: {latest_stats.glsavepct:.1f}%")
                write(f"        Shutout Periods: {latest_stats.glsoperiods}")
                write(f"        Goals Saved: {latest_stats.goals_saved}")
                write(f"        Save %: {latest_stats.save_percentage:.1f}%")
                
                write("\n        Breakaways:")
                write(f"          Saves: {latest_stats.glbrksaves}")
                write(f"          Shots: {latest_stats.glbrkshots}")
                write(f"          Save %: {latest_stats.glbrksavepct:.1f}%")
                
                write("\n        Penalty Shots:")
                write(f"          Saves: {latest_stats.glpensaves}")
                write(f"          Shots: {latest_stats.glpenshots}")
                write(f"          Save %: {latest_stats.glpensavepct:.1f}%")
                
                write("\n        Other:")
                write(f"          Desperation Saves: {latest_stats.gldsaves}")
                write(f"          Poke Checks: {latest_stats.glpokechecks}")
                write(f"          PK Clear Zone: {latest_stats.glpkclearzone}")


def main() -> None:
    """Analyze season data structure with real match data."""
    print("Loading match data...")
    with open("live_tests/output/ea_response.json") as f:
        matches = json.load(f)
    
    # Use first match
    match_data = matches[0]
    match = Match.model_validate(match_data)
    
    print("\nCreating season...")
    season = create_season()
    
    print("\nProcessing match data...")
    process_match_data(season, match)
    
    # Create league data with season
    league = LeagueData()
    league.seasons[f"season_{season.season_id}"] = season
    
    # Create analysis
    analysis = DataStructureAnalysis(
        raw_match=match_data,
        match=match,
        league=league
    )
    
    # Save JSON structure using Pydantic's serialization
    json_file = "live_tests/output/season_structure.json"
    with open(json_file, "w") as f:
        json.dump(analysis.model_dump(mode="json"), f, indent=2)
    print(f"\nJSON data structure saved to {json_file}")
    
    # Save human-readable summary
    summary_file = "live_tests/output/season_summary.txt"
    with open(summary_file, "w") as f:
        write_human_readable_summary(season, match, f)
    print(f"Human-readable summary saved to {summary_file}")


if __name__ == "__main__":
    main() 