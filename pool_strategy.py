from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PoolStrategyScore:
    team: str
    win_probability: float
    pick_popularity: float
    elimination_leverage: float
    leverage_ratio: float
    strategy_score: float


def calculate_pool_strategy_score(
    team: str,
    win_probability: float,
    pick_popularity: float,
) -> PoolStrategyScore:
    """
    Score a Survivor pick using both safety and field leverage.

    win_probability:
        Probability our team wins.

    pick_popularity:
        Estimated fraction of the pool selecting this team.
        Example: 0.35 = 35%.
    """

    if not 0.0 <= win_probability <= 1.0:
        raise ValueError(
            "win_probability must be between 0 and 1."
        )

    if not 0.0 <= pick_popularity <= 1.0:
        raise ValueError(
            "pick_popularity must be between 0 and 1."
        )

    loss_probability = 1.0 - win_probability

    elimination_leverage = (
        pick_popularity * loss_probability
    )

    leverage_ratio = (
        win_probability
        / max(pick_popularity, 0.01)
    )

    # Safety remains dominant.
    #
    # The leverage adjustment is deliberately modest so
    # we do not make reckless contrarian Survivor picks.
    strategy_score = (
        win_probability
        * (
            1.0
            + 0.25 * elimination_leverage
        )
    )

    return PoolStrategyScore(
        team=team,
        win_probability=win_probability,
        pick_popularity=pick_popularity,
        elimination_leverage=elimination_leverage,
        leverage_ratio=leverage_ratio,
        strategy_score=strategy_score,
    )


def rank_pool_options(
    win_probabilities: Dict[str, float],
    pick_popularity: Dict[str, float],
) -> List[PoolStrategyScore]:
    scores = []

    for team, win_probability in win_probabilities.items():
        popularity = pick_popularity.get(
            team,
            0.0,
        )

        score = calculate_pool_strategy_score(
            team=team,
            win_probability=win_probability,
            pick_popularity=popularity,
        )

        scores.append(score)

    return sorted(
        scores,
        key=lambda item: item.strategy_score,
        reverse=True,
    )


def build_pool_strategy_report(
    scores: List[PoolStrategyScore],
) -> str:
    lines = [
        "=== POOL STRATEGY ===",
        "",
    ]

    for rank, score in enumerate(
        scores,
        start=1,
    ):
        lines.extend(
            [
                f"{rank}. {score.team}",
                (
                    "   Win probability: "
                    f"{score.win_probability:.1%}"
                ),
                (
                    "   Projected ownership: "
                    f"{score.pick_popularity:.1%}"
                ),
                (
                    "   Elimination leverage: "
                    f"{score.elimination_leverage:.2%}"
                ),
                (
                    "   Strategy score: "
                    f"{score.strategy_score:.4f}"
                ),
                "",
            ]
        )

    return "\n".join(lines)
