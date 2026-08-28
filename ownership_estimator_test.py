from dataclasses import dataclass

from ownership_estimator import (
    build_ownership_report,
    estimate_survivor_ownership,
)


@dataclass
class TestGame:
    home_team: str
    away_team: str
    home_win_prob: float
    away_win_prob: float


def main():
    games = [
        TestGame(
            home_team="LAC",
            away_team="LV",
            home_win_prob=0.812,
            away_win_prob=0.188,
        ),
        TestGame(
            home_team="BUF",
            away_team="NYJ",
            home_win_prob=0.790,
            away_win_prob=0.210,
        ),
        TestGame(
            home_team="PHI",
            away_team="NYG",
            home_win_prob=0.775,
            away_win_prob=0.225,
        ),
        TestGame(
            home_team="JAX",
            away_team="TEN",
            home_win_prob=0.760,
            away_win_prob=0.240,
        ),
        TestGame(
            home_team="DAL",
            away_team="WAS",
            home_win_prob=0.650,
            away_win_prob=0.350,
        ),
    ]

    estimates = estimate_survivor_ownership(
        games
    )

    print(
        build_ownership_report(
            estimates
        )
    )

    total_ownership = sum(
        estimate.estimated_ownership
        for estimate in estimates
    )

    assert abs(total_ownership - 1.0) < 0.000001
    assert estimates[0].team == "LAC"

    print()
    print("Ownership estimator test: PASS")


if __name__ == "__main__":
    main()
