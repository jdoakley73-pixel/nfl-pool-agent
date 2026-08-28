from typing import List

from data_provider import RawGameData, build_games
from espn_provider import fetch_nfl_week
from market import apply_market_to_games
from odds_provider import fetch_event_odds
from season_planner import best_survivor_paths
from state import load_state
from survivor_decision import (
    analyze_survivor_paths,
    build_survivor_decision_report,
)


SEASON = 2026
END_WEEK = 18


def add_live_odds(
    raw_games: List[RawGameData],
) -> List[RawGameData]:
    games_with_odds = []

    for game in raw_games:
        if not game.event_id:
            continue

        odds = fetch_event_odds(game.event_id)

        if odds is None:
            continue

        game.away_moneyline = odds["away_moneyline"]
        game.home_moneyline = odds["home_moneyline"]
        game.spread = odds["spread"]
        game.total = odds["total"]

        games_with_odds.append(game)

    return games_with_odds


def fetch_week_with_odds(
    season: int,
    week: int,
):
    raw_games = fetch_nfl_week(
        season=season,
        week=week,
    )

    raw_games = add_live_odds(raw_games)

    games = build_games(raw_games)

    return apply_market_to_games(games)


def main():
    state = load_state()

    current_week = state.current_week

    print(
        f"\n=== WEEKLY SURVIVOR REPLANNER ===\n"
        f"Season: {SEASON}\n"
        f"Current week: {current_week}\n"
        f"Used teams: "
        f"{sorted(state.survivor_used_teams)}\n"
    )

    all_games = []

    for week in range(
        current_week,
        END_WEEK + 1,
    ):
        games = fetch_week_with_odds(
            season=SEASON,
            week=week,
        )

        print(
            f"Week {week}: "
            f"{len(games)} games with odds"
        )

        all_games.extend(games)

    paths = best_survivor_paths(
        games=all_games,
        start_week=current_week,
        end_week=END_WEEK,
        used_teams=state.survivor_used_teams,
        top_n=500,
    )

    if not paths:
        raise RuntimeError(
            "No valid Survivor paths were generated."
        )

    decision = analyze_survivor_paths(paths)

    print()
    print(
        build_survivor_decision_report(
            decision
        )
    )

    print()
    print("=== BEST REMAINING PATH ===")
    print()

    best_path = paths[0]

    for week in sorted(best_path.picks):
        print(
            f"Week {week}: "
            f"{best_path.picks[week]}"
        )


if __name__ == "__main__":
    main()
