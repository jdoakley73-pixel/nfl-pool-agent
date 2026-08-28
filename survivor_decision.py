from dataclasses import dataclass
from typing import Dict, List

from season_planner import SurvivorPath
from decision_confidence import (
    classify_decision_confidence,
    decision_confidence_reason,
)

@dataclass
class SurvivorDecision:
    recommended_team: str
    best_path_probability: float
    best_paths_by_first_pick: Dict[str, float]
    opportunity_costs: Dict[str, float]


def first_pick(path: SurvivorPath) -> str | None:
    if not path.picks:
        return None

    first_week = min(path.picks)

    return path.picks[first_week]


def analyze_survivor_paths(
    paths: List[SurvivorPath],
) -> SurvivorDecision:
    """
    Compare the strongest overall Survivor path against the
    strongest path available for each possible first-week pick.
    """

    if not paths:
        raise ValueError("No Survivor paths supplied.")

    best_overall = paths[0]
    recommended_team = first_pick(best_overall)

    if recommended_team is None:
        raise ValueError("Best path has no picks.")

    best_paths_by_first_pick: Dict[str, float] = {}

    for path in paths:
        team = first_pick(path)

        if team is None:
            continue

        current_best = best_paths_by_first_pick.get(
            team,
            0.0,
        )

        if path.survival_probability > current_best:
            best_paths_by_first_pick[team] = (
                path.survival_probability
            )

    opportunity_costs = {}

    for team, probability in best_paths_by_first_pick.items():
        opportunity_costs[team] = (
            best_overall.survival_probability
            - probability
        )

    return SurvivorDecision(
        recommended_team=recommended_team,
        best_path_probability=(
            best_overall.survival_probability
        ),
        best_paths_by_first_pick=best_paths_by_first_pick,
        opportunity_costs=opportunity_costs,
    )


def build_survivor_decision_report(
    decision: SurvivorDecision,
) -> str:
    lines = [
        "=== SURVIVOR DECISION ANALYSIS ===",
        "",
        f"Recommended Week 1 pick: "
        f"{decision.recommended_team}",
        "",
        f"Best path survival probability: "
        f"{decision.best_path_probability:.4%}",
        "",
        "Best path by Week 1 choice:",
    ]

    ranked = sorted(
        decision.best_paths_by_first_pick.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_probability = ranked[0][1]

    for team, probability in ranked:
        cost = best_probability - probability

        if best_probability > 0:
            relative_cost = cost / best_probability
        else:
            relative_cost = 0.0

        lines.append(
            f"{team}: {probability:.4%} "
            f"| Cost vs best: {cost:.4%} "
            f"| Relative gap: {relative_cost:.2%}"
        )

    if len(ranked) >= 2:
        first_team, first_probability = ranked[0]
        second_team, second_probability = ranked[1]

        confidence = classify_decision_confidence(
            first_probability,
            second_probability,
        )

        confidence_reason = decision_confidence_reason(
            first_team,
            second_team,
            first_probability,
            second_probability,
        )
        
        absolute_edge = (
            first_probability
            - second_probability
        )

        relative_edge = (
            absolute_edge / second_probability
            if second_probability > 0
            else 0.0
        )

                lines.extend(
            [
                "",
                "Decision margin:",
                (
                    f"{first_team} over {second_team}: "
                    f"{absolute_edge:.4%} absolute "
                    f"| {relative_edge:.2%} relative"
                ),
                "",
                "=== SURVIVOR RECOMMENDATION ===",
                "",
                f"PRIMARY PICK: {first_team}",
                f"DECISION CONFIDENCE: {confidence}",
                f"ALTERNATIVE: {second_team}",
                "",
                confidence_reason,
            ]
                )
    return "\n".join(lines)
