from datetime import datetime

from data_provider import RawGameData, build_games
from future_value import calculate_future_values
from market import apply_market_to_games
from pickem import build_pickem_card
from survivor import recommend_survivor_pick


def main():
    # Fake current-week games for testing.
    current_games_raw = [
        RawGameData(
            week=1,
            kickoff=datetime(2026, 9, 10, 19, 20),
            away_team="Detroit Lions",
            home_team="Minnesota Vikings",
            away_moneyline=145,
            home_moneyline=-170,
            total=47.5,
        ),
        RawGameData(
            week=1,
            kickoff=datetime(2026, 9, 13, 12, 0),
            away_team="Cleveland Browns",
            home_team="Baltimore Ravens",
            away_moneyline=300,
            home_moneyline=-380,
            total=43.5,
        ),
        RawGameData(
            week=1,
            kickoff=datetime(2026, 9, 13, 15, 25),
            away_team="Las Vegas Raiders",
            home_team="Kansas City Chiefs",
            away_moneyline=400,
            home_moneyline=-520,
            total=46.0,
        ),
    ]

    games = build_games(current_games_raw)
    games = apply_market_to_games(games)

    print("\n=== PICK'EM CARD ===")

    pickem_card = build_pickem_card(games)

    for recommendation in pickem_card:
        print(
            f"{recommendation.matchup}: "
            f"{recommendation.pick} | "
            f"{recommendation.win_probability:.1%} | "
            f"{recommendation.confidence}"
        )

    # Fake future games so we can test Survivor preservation.
    future_games_raw = [
        RawGameData(
            week=2,
            kickoff=datetime(2026, 9, 20, 12, 0),
            away_team="New York Jets",
            home_team="Kansas City Chiefs",
            away_moneyline=475,
            home_moneyline=-650,
        ),
        RawGameData(
            week=3,
            kickoff=datetime(2026, 9, 27, 12, 0),
            away_team="Cleveland Browns",
            home_team="Baltimore Ravens",
            away_moneyline=325,
            home_moneyline=-425,
        ),
    ]

    future_games = build_games(future_games_raw)
    future_games = apply_market_to_games(future_games)

    future_values = calculate_future_values(
        future_games=future_games,
        current_week=1,
    )

    survivor_rankings = recommend_survivor_pick(
        games=games,
        used_teams=set(),
        future_values=future_values,
    )

    print("\n=== SURVIVOR RANKINGS ===")

    for rank, recommendation in enumerate(
        survivor_rankings,
        start=1,
    ):
        print(
            f"{rank}. {recommendation.team} over "
            f"{recommendation.opponent} | "
            f"Win: {recommendation.win_probability:.1%} | "
            f"Future value: {recommendation.future_value:.3f} | "
            f"Score: {recommendation.survivor_score:.3f}"
        )


if __name__ == "__main__":
    main()
