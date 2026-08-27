from espn_provider import fetch_nfl_week


def main():
    season = 2026
    week = 1

    games = fetch_nfl_week(
        season=season,
        week=week,
    )

    print(
        f"\n=== LIVE NFL SCHEDULE TEST ===\n"
        f"Season: {season}\n"
        f"Week: {week}\n"
        f"Games found: {len(games)}\n"
    )

    for game in games:
        print(
            f"{game.away_team} @ {game.home_team} | "
            f"{game.kickoff.isoformat()}"
        )

    if not games:
        raise RuntimeError(
            "No games returned from live NFL schedule provider."
        )


if __name__ == "__main__":
    main()
