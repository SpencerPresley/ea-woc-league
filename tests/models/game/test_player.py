"""Test cases for player models."""

from typing import Dict, List

from ea_nhl_stats.models.game.player import AggregateStats, PlayerStats


def test_player_stats_model(game_response_data: List[Dict]) -> None:
    """
    Test PlayerStats model validation and data conversion.

    Args:
        game_response_data: Sample game response data
    """
    # Get first player stats from first match
    first_club_id = next(iter(game_response_data[0]["players"]))
    first_player_id = next(iter(game_response_data[0]["players"][first_club_id]))
    player_data = game_response_data[0]["players"][first_club_id][first_player_id]

    player = PlayerStats.model_validate(player_data)

    # Test numeric field conversion
    assert isinstance(player.class_, int)
    assert isinstance(player.rating_defense, float)
    assert isinstance(player.rating_offense, float)
    assert isinstance(player.rating_teamplay, float)
    assert isinstance(player.sk_assists, int)
    assert isinstance(player.sk_faceoffs_won, int)
    assert isinstance(player.sk_giveaways, int)
    assert isinstance(player.sk_goals, int)
    assert isinstance(player.sk_hits, int)
    assert isinstance(player.sk_penalty_minutes, int)
    assert isinstance(player.sk_plus_minus, int)
    assert isinstance(player.sk_shots, int)
    assert isinstance(player.sk_takeaways, int)


def test_aggregate_stats_model(game_response_data: List[Dict]) -> None:
    """
    Test AggregateStats model validation and data conversion.

    Args:
        game_response_data: Sample game response data
    """
    # Get first aggregate stats from first match
    first_club_id = next(iter(game_response_data[0]["aggregate"]))
    aggregate_data = game_response_data[0]["aggregate"][first_club_id]

    aggregate = AggregateStats.model_validate(aggregate_data)

    # Test that it inherits all fields from PlayerStats
    assert isinstance(aggregate.class_, int)
    assert isinstance(aggregate.rating_defense, float)
    assert isinstance(aggregate.rating_offense, float)
    assert isinstance(aggregate.rating_teamplay, float)
    assert isinstance(aggregate.sk_assists, int)
    assert isinstance(aggregate.sk_faceoffs_won, int)
    assert isinstance(aggregate.sk_giveaways, int)
    assert isinstance(aggregate.sk_goals, int)
    assert isinstance(aggregate.sk_hits, int)
    assert isinstance(aggregate.sk_penalty_minutes, int)
    assert isinstance(aggregate.sk_plus_minus, int)
    assert isinstance(aggregate.sk_shots, int)
    assert isinstance(aggregate.sk_takeaways, int) 