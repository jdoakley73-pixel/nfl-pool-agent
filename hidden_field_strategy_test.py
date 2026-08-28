from datetime import datetime

from hidden_field_strategy import (
    build_hidden_field_decision,
    rank_hidden_field_options,
)
from models import NFLGame
from season_planner import SurvivorPath


def make_game(home, away, home_prob, away_prob):
    return NFLGame(
        week=1,
        kickoff=datetime(2026, 9, 13, 12, 0),
        home_team=home,
        away_team=away,
        home_win_prob=home_prob,
        away_win_prob=away_prob,
    )


def main():
    games = [
        make_game("LAC", "LV", 0.812, 0.188),
        make_game("JAX", "TEN", 0.760, 0.240),
    ]
    paths = [
        SurvivorPath(picks={1: "LAC"}, survival_probability=0.001466),
        SurvivorPath(picks={1: "JAX"}, survival_probability=0.001451),
    ]
    ownership = {"LAC": 0.245, "JAX": 0.156}

    ranked = rank_hidden_field_options(
        week=1,
        current_week_games=games,
        paths=paths,
        ownership_by_team=ownership,
        pool_size=75,
    )
    assert ranked[0].team == "LAC"
    assert ranked[0].strategy_score > ranked[1].strategy_score

    decision = build_hidden_field_decision(
        week=1,
        current_week_games=games,
        paths=paths,
        ownership_by_team=ownership,
        pool_size=75,
    )
    assert decision.recommended_team == "LAC"
    assert decision.alternative_team == "JAX"

    print("Hidden-field strategy test passed.")
    print(f"Recommended: {decision.recommended_team}")
    print(f"Alternative: {decision.alternative_team}")
    print(f"Verdict: {decision.verdict}")
    print(f"Reason: {decision.reason}")


if __name__ == "__main__":
    main()
