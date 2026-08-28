from dataclasses import asdict
from typing import Dict, List

from hidden_field_strategy import build_hidden_field_decision
from ownership_estimator import estimate_survivor_ownership
from pickem import build_pickem_card
from season_planner import best_survivor_paths
from state import PoolState
from weekly_replanner import END_WEEK, SEASON, fetch_week_with_odds


def build_command_center_data(
    state: PoolState,
    pool_size: int = 75,
) -> Dict[str, object]:
    """Build one snapshot for the Survivor and Pick'em dashboard tabs."""
    current_week = state.current_week
    all_games = []

    for week in range(current_week, END_WEEK + 1):
        all_games.extend(fetch_week_with_odds(SEASON, week))

    current_week_games = [
        game for game in all_games if game.week == current_week
    ]
    if not current_week_games:
        raise RuntimeError(
            f"No games with odds are available for Week {current_week}."
        )

    pickem_card = build_pickem_card(current_week_games)

    paths = best_survivor_paths(
        games=all_games,
        start_week=current_week,
        end_week=END_WEEK,
        used_teams=state.survivor_used_teams,
        top_n=500,
    )
    if not paths:
        raise RuntimeError("No valid Survivor paths were generated.")

    ownership_estimates = estimate_survivor_ownership(
        games=current_week_games,
        used_teams=state.survivor_used_teams,
    )
    ownership_by_team = {
        estimate.team: estimate.estimated_ownership
        for estimate in ownership_estimates
    }

    survivor_decision = build_hidden_field_decision(
        week=current_week,
        current_week_games=current_week_games,
        paths=paths,
        ownership_by_team=ownership_by_team,
        pool_size=pool_size,
    )

    best_path = paths[0]

    return {
        "season": state.season,
        "current_week": current_week,
        "pool_size": pool_size,
        "survivor_alive": state.survivor_alive,
        "used_teams": sorted(state.survivor_used_teams),
        "survivor_picks": dict(state.survivor_picks),
        "survivor_decision": asdict(survivor_decision),
        "best_path": dict(best_path.picks),
        "best_path_probability": best_path.survival_probability,
        "pickem_card": [asdict(item) for item in pickem_card],
        "pickem_season_points": state.pickem_season_points,
    }
