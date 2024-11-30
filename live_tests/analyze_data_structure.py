"""Script to analyze and output our data structures.

This script loads EA NHL match data and processes it through our models,
then outputs a complete picture of our data structures including:
1. Raw match data from EA
2. Processed match/club/player stats
3. League team and player tracking
4. Future user integration points

The output helps us:
1. Verify our current data model
2. Plan database schema
3. Identify any missing relationships
4. Consider user integration points
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ea_nhl_stats.models.game.ea_match import Match
from ea_nhl_stats.models.game.ea_club_stats import ClubStats
from ea_nhl_stats.models.game.ea_player_stats import PlayerStats
from ea_nhl_stats.league.models.team import LeagueTeam
from ea_nhl_stats.league.models.player import LeaguePlayer
from ea_nhl_stats.league.models.history import SeasonStats
from ea_nhl_stats.league.enums.types import Position, ManagerRole


# Future user model to consider
class User(BaseModel):
    """User model for website integration."""
    
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    discord_id: Optional[str] = None
    ea_id: Optional[str] = None  # Link to EA player ID
    created_at: datetime = Field(default_factory=datetime.now)
    is_admin: bool = False
    is_manager: bool = False


class DataStructureAnalysis(BaseModel):
    """Complete picture of our data model relationships."""
    
    # Raw EA data
    raw_match: Dict
    
    # Processed EA models
    match: Match
    club_stats: Dict[str, ClubStats]  # club_id -> stats
    player_stats: Dict[str, Dict[str, PlayerStats]]  # club_id -> player_id -> stats
    
    # League models
    teams: Dict[str, LeagueTeam]  # ea_club_id -> team
    players: Dict[str, LeaguePlayer]  # ea_id -> player
    
    # Future user integration
    users: Dict[str, User]  # ea_id -> user


def analyze_match(match_data: Dict) -> DataStructureAnalysis:
    """Analyze a match and show all data relationships."""
    # Parse match
    match = Match.model_validate(match_data)
    
    # Create test teams
    teams = {}
    for club_id, club in match.clubs.items():
        team = LeagueTeam(
            name=club.details.name,
            current_season=1,
            ea_club_id=club_id
        )
        teams[club_id] = team
        
        # Add match to team history
        team.add_match(match)
    
    # Create test players
    players = {}
    for club_id, club_players in match.players.items():
        for player_id, stats in club_players.items():
            # Create player with proper role
            is_manager = True  # In real app, would check against manager list
            player = LeaguePlayer(
                name=stats.player_name,
                position=Position.CENTER,  # Would come from preferences
                role=ManagerRole.GM if is_manager else None,  # Would be set on signup
                current_season=1,
                ea_id=player_id,
                ea_name=stats.player_name,
                ea_stats=stats  # Link current game stats
            )
            
            # Add player to team
            teams[club_id].add_player(player.id)
            if is_manager:
                teams[club_id].add_manager(player.id)
            
            # Update season stats with game stats
            if 1 not in player.season_stats:
                player.season_stats[1] = SeasonStats(season=1)
            player.season_stats[1].game_stats[match.match_id] = stats
            player.season_stats[1].games_played += 1
            player.season_stats[1].positions.add(player.position)
            
            players[player_id] = player
    
    # Create test users (future integration)
    users = {}
    for player_id, player in players.items():
        user = User(
            username=player.ea_name,
            email=f"{player.ea_name}@example.com",  # Would come from signup
            ea_id=player_id,
            is_manager=player.role is not None
        )
        users[player_id] = user
    
    return DataStructureAnalysis(
        raw_match=match_data,
        match=match,
        club_stats=match.clubs,
        player_stats=match.players,
        teams=teams,
        players=players,
        users=users
    )


def main():
    """Analyze data structure and output results."""
    print("Loading match data...")
    with open("live_tests/output/ea_response.json") as f:
        matches = json.load(f)
    
    # Analyze first match
    match_data = matches[0]
    analysis = analyze_match(match_data)
    
    # Output analysis
    output = {
        "raw_match": analysis.raw_match,
        "processed_data": {
            "match": analysis.match.model_dump(),
            "club_stats": {
                club_id: stats.model_dump()
                for club_id, stats in analysis.club_stats.items()
            },
            "player_stats": {
                club_id: {
                    player_id: stats.model_dump()
                    for player_id, stats in club_players.items()
                }
                for club_id, club_players in analysis.player_stats.items()
            }
        },
        "league_data": {
            "teams": {
                team_id: team.model_dump()
                for team_id, team in analysis.teams.items()
            },
            "players": {
                player_id: player.model_dump()
                for player_id, player in analysis.players.items()
            }
        },
        "future_user_data": {
            "users": {
                user_id: user.model_dump()
                for user_id, user in analysis.users.items()
            }
        }
    }
    
    # Save to file
    output_file = "live_tests/output/data_structure.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)  # Handle UUID serialization
    
    print(f"\nData structure analysis saved to {output_file}")
    print("\nKey relationships:")
    print("1. EA Match -> Clubs -> Players (raw game data)")
    print("2. League Teams -> Players & Managers (via UUID)")
    print("3. Users -> Players (via EA ID)")
    print("4. Teams -> Match History (via EA club ID)")
    print("5. Players -> Season Stats -> Game Stats (via match ID)")
    print("6. Players -> Current Game Stats (via EA player stats)")


if __name__ == "__main__":
    main() 