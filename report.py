from typing import List

from pickem import PickemRecommendation
from survivor import SurvivorRecommendation


def build_pickem_report(
    recommendations: List[PickemRecommendation],
) -> str:
    lines = [
        "=== PICK'EM RECOMMENDATIONS ===",
        "",
    ]

    for recommendation in recommendations:
        leverage = (
            " | LEVERAGE"
            if recommendation.leverage_flag
            else ""
        )

        lines.append(
            f"{recommendation.matchup}"
        )
        lines.append(
            f"Pick: {recommendation.pick}"
        )
        lines.append(
            f"Win probability: "
            f"{recommendation.win_probability:.1%}"
        )
        lines.append(
            f"Confidence: "
            f"{recommendation.confidence}{leverage}"
        )
        lines.append(
            f"Reason: {recommendation.reason}"
        )
        lines.append("")

    return "\n".join(lines)


def build_survivor_report(
    recommendations: List[SurvivorRecommendation],
    top_n: int = 5,
) -> str:
    lines = [
        "=== SURVIVOR RECOMMENDATIONS ===",
        "",
    ]

    for rank, recommendation in enumerate(
        recommendations[:top_n],
        start=1,
    ):
        lines.append(
            f"{rank}. {recommendation.team} "
            f"over {recommendation.opponent}"
        )
        lines.append(
            f"Win probability: "
            f"{recommendation.win_probability:.1%}"
        )
        lines.append(
            f"Future value: "
            f"{recommendation.future_value:.3f}"
        )
        lines.append(
            f"Survivor score: "
            f"{recommendation.survivor_score:.3f}"
        )
        lines.append(
            f"Reason: {recommendation.reason}"
        )
        lines.append("")

    return "\n".join(lines)


def build_full_report(
    pickem_recommendations: List[PickemRecommendation],
    survivor_recommendations: List[SurvivorRecommendation],
) -> str:
    return (
        build_pickem_report(pickem_recommendations)
        + "\n"
        + build_survivor_report(
            survivor_recommendations
        )
    )
