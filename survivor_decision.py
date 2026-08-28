from dataclasses import dataclass
from typing import Dict, List

from season_planner import SurvivorPath


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
        f"{decision.best_path_probability:.1%}",
        "",
        "Best path by Week 1 choice:",
    ]

    ranked = sorted(
        decision.best_paths_by_first_pick.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for team, probability in ranked:
        cost = decision.opportunity_costs[team]

        lines.append(
            f"{team}: {probability:.1%} "
            f"| Cost vs best: {cost:.1%}"
        )

    return "\n".join(lines)
