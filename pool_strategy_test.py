from pool_strategy import (
    build_pool_strategy_report,
    rank_pool_options,
)


def main():
    win_probabilities = {
        "LAC": 0.812,
        "JAX": 0.760,
        "BUF": 0.790,
        "PHI": 0.775,
    }

    pick_popularity = {
        "LAC": 0.42,
        "JAX": 0.08,
        "BUF": 0.28,
        "PHI": 0.12,
    }

    scores = rank_pool_options(
        win_probabilities=win_probabilities,
        pick_popularity=pick_popularity,
    )

    print(
        build_pool_strategy_report(
            scores
        )
    )

    assert len(scores) == 4

    assert scores[0].strategy_score > 0

    print("Pool strategy test: PASS")


if __name__ == "__main__":
    main()
