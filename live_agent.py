from typing import List

from data_provider import RawGameData, build_games
from espn_provider import fetch_nfl_week
from future_value import calculate_future_values
from market import apply_market_to_games
from odds_provider import fetch_event_odds
from pickem import build_pickem_card
from report import build_full_report
from survivor import recommend_survivor_pick


SEASON = 2026
CURRENT_WEEK = 1
LOOKAHEAD_WEEKS = 4


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
    print(
        f"\nNFL POOL AGENT — "
        f"{SEASON} WEEK {CURRENT_WEEK}\n"
    )

    current_games = fetch_week_with_odds(
        season=SEASON,
        week=CURRENT_WEEK,
    )

    if not current_games:
        raise RuntimeError(
            "No current-week games with odds were found."
        )

    pickem_recommendations = build_pickem_card(
        current_games
    )

    future_games = []

    final_future_week = min(
        18,
        CURRENT_WEEK + LOOKAHEAD_WEEKS,
    )

    for week in range(
        CURRENT_WEEK + 1,
        final_future_week + 1,
    ):
        try:
            games = fetch_week_with_odds(
                season=SEASON,
                week=week,
            )
            future_games.extend(games)
        except Exception as exc:
            print(
                f"Future Week {week} unavailable: {exc}"
            )

    future_values = calculate_future_values(
        future_games=future_games,
        current_week=CURRENT_WEEK,
    )

    survivor_recommendations = recommend_survivor_pick(
        games=current_games,
        used_teams=set(),
        future_values=future_values,
    )

    report = build_full_report(
        pickem_recommendations=pickem_recommendations,
        survivor_recommendations=survivor_recommendations,
    )

    print(report)


if __name__ == "__main__":
    main()
