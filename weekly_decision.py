from dataclasses import dataclass
from typing import List, Optional

from decision_confidence import classify_decision_confidence
from models import NFLGame
from season_planner import SurvivorPath
from survivor_decision import analyze_survivor_paths


@dataclass
class WeeklySurvivorDecision:
    week: int
    primary_team: str
    alternative_team: Optional[str]
    primary_win_probability: float
    alternative_win_probability: Optional[float]
    season_path_probability: float
    confidence: str
    recommendation: str


def find_team_probability(
    games: List[NFLGame],
    team: str,
) -> float:
    for game in games:
        if game.home_team == team:
            return game.home_win_prob

        if game.away_team == team:
            return game.away_win_prob

    raise ValueError(
        f"Could not find current-week game for {team}."
    )


def build_weekly_survivor_decision(
    week: int,
    current_week_games: List[NFLGame],
    paths: List[SurvivorPath],
) -> WeeklySurvivorDecision:
    if not paths:
        raise ValueError("No Survivor paths supplied.")

    decision = analyze_survivor_paths(paths)

    ranked = sorted(
        decision.best_paths_by_first_pick.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    primary_team = ranked[0][0]

    alternative_team = (
        ranked[1][0]
        if len(ranked) >= 2
        else None
    )

    primary_win_probability = find_team_probability(
        current_week_games,
        primary_team,
    )

    alternative_win_probability = None

    if alternative_team is not None:
        alternative_win_probability = find_team_probability(
            current_week_games,
            alternative_team,
        )

    if alternative_team is None:
        confidence = "STRONG"
    else:
        confidence = classify_decision_confidence(
            ranked[0][1],
            ranked[1][1],
        )

    recommendation = build_action_recommendation(
        confidence=confidence,
        primary_win_probability=primary_win_probability,
        alternative_win_probability=alternative_win_probability,
    )

    return WeeklySurvivorDecision(
        week=week,
        primary_team=primary_team,
        alternative_team=alternative_team,
        primary_win_probability=primary_win_probability,
        alternative_win_probability=alternative_win_probability,
        season_path_probability=ranked[0][1],
        confidence=confidence,
        recommendation=recommendation,
    )


def build_action_recommendation(
    confidence: str,
    primary_win_probability: float,
    alternative_win_probability: Optional[float],
) -> str:
    if confidence == "STRONG":
        return "LOCK"

    if confidence == "LEAN":
        return "LEAN"

    if alternative_win_probability is None:
        return "LOCK"

    current_week_edge = (
        primary_win_probability
        - alternative_win_probability
    )

    if abs(current_week_edge) <= 0.02:
        return "WAIT"

    return "LEAN"


def build_weekly_decision_report(
    decision: WeeklySurvivorDecision,
) -> str:
    lines = [
        "=== WEEKLY SURVIVOR DECISION ===",
        "",
        f"Week: {decision.week}",
        f"Primary: {decision.primary_team}",
        (
            f"Primary current win probability: "
            f"{decision.primary_win_probability:.1%}"
        ),
        f"Decision confidence: {decision.confidence}",
        f"Action: {decision.recommendation}",
        "",
    ]

    if decision.alternative_team is not None:
        lines.extend(
            [
                f"Alternative: {decision.alternative_team}",
                (
                    f"Alternative current win probability: "
                    f"{decision.alternative_win_probability:.1%}"
                ),
                "",
            ]
        )

    lines.extend(
        [
            (
                "Best remaining-season path probability: "
                f"{decision.season_path_probability:.4%}"
            ),
        ]
    )

    return "\n".join(lines)
