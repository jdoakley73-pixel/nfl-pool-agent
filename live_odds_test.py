from espn_provider import fetch_nfl_week
from odds_provider import fetch_event_odds


def main():
    season = 2026
    week = 1

    games = fetch_nfl_week(
        season=season,
        week=week,
    )

    print("\n=== LIVE NFL ODDS TEST ===")
    print(f"Season: {season}")
    print(f"Week: {week}")
    print(f"Games found: {len(games)}")
    print()

    odds_found = 0

    for game in games:
        if not game.event_id:
            print(
                f"{game.away_team} @ {game.home_team} | "
                f"NO EVENT ID"
            )
            continue

        odds = fetch_event_odds(game.event_id)

        if odds is None:
            print(
                f"{game.away_team} @ {game.home_team} | "
                f"NO ODDS AVAILABLE"
            )
            continue

        odds_found += 1

        print(
            f"{game.away_team} @ {game.home_team} | "
            f"{odds['provider']}"
        )
        print(
            f"  Away ML: {odds['away_moneyline']} | "
            f"Win: {odds['away_win_probability']:.1%}"
        )
        print(
            f"  Home ML: {odds['home_moneyline']} | "
            f"Win: {odds['home_win_probability']:.1%}"
        )
        print(
            f"  Spread: {odds['spread']} | "
            f"Total: {odds['total']}"
        )
        print()

    print(
        f"Odds available for "
        f"{odds_found}/{len(games)} games."
    )

    if odds_found == 0:
        raise RuntimeError(
            "No live odds were returned for any Week 1 games."
        )


if __name__ == "__main__":
    main()
