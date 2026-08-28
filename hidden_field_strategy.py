from dataclasses import dataclass
from typing import Dict, List, Optional

from models import NFLGame
from season_planner import SurvivorPath


DEFAULT_POOL_SIZE = 75


@dataclass
class HiddenFieldScore:
    team: str
    win_probability: float
    estimated_ownership: float
    expected_entries: float
    expected_field_eliminated_if_loss: float
    season_path_probability: float
    relative_season_value: float
    strategy_score: float


@dataclass
class HiddenFieldDecision:
    recommended_team: str
    alternative_team: Optional[str]
    recommended_score: HiddenFieldScore
    alternative_score: Optional[HiddenFieldScore]
    verdict: str
    reason: str


def _team_probability(games: List[NFLGame], team: str) -> float:
    for game in games:
        if game.home_team == team:
            return game.home_win_prob
        if game.away_team == team:
            return game.away_win_prob
    raise ValueError(f"Could not find current-week game for {team}.")


def _best_path_by_first_pick(
    paths: List[SurvivorPath],
    week: int,
) -> Dict[str, float]:
    best: Dict[str, float] = {}
    for path in paths:
        team = path.picks.get(week)
        if team is None:
            continue
        best[team] = max(
            best.get(team, 0.0),
            path.survival_probability,
        )
    return best


def rank_hidden_field_options(
    week: int,
    current_week_games: List[NFLGame],
    paths: List[SurvivorPath],
    ownership_by_team: Dict[str, float],
    pool_size: int = DEFAULT_POOL_SIZE,
) -> List[HiddenFieldScore]:
    """Rank Survivor choices while keeping survival as the dominant goal.

    Ownership is estimated, not observed. The model therefore gives it a
    deliberately modest influence. Season-path value is normalized against
    the best available first-pick path so its scale is stable week to week.
    """
    if pool_size <= 0:
        raise ValueError("pool_size must be positive.")

    path_by_team = _best_path_by_first_pick(paths, week)
    if not path_by_team:
        return []

    best_path_probability = max(path_by_team.values())
    scores: List[HiddenFieldScore] = []

    for team, season_probability in path_by_team.items():
        win_probability = _team_probability(current_week_games, team)
        ownership = ownership_by_team.get(team, 0.0)
        expected_entries = ownership * pool_size
        expected_field_eliminated_if_loss = (
            expected_entries * (1.0 - win_probability)
        )
        relative_season_value = (
            season_probability / best_path_probability
            if best_path_probability > 0
            else 0.0
        )

        # Survival is intentionally dominant. A contrarian option should not
        # overcome a meaningful safety gap merely because ownership is lower.
        # Season planning receives the next-largest weight; ownership is a
        # tiebreaker/edge, not the foundation of the recommendation.
        strategy_score = (
            0.72 * win_probability
            + 0.23 * relative_season_value
            + 0.05 * (1.0 - ownership)
        )

        scores.append(
            HiddenFieldScore(
                team=team,
                win_probability=win_probability,
                estimated_ownership=ownership,
                expected_entries=expected_entries,
                expected_field_eliminated_if_loss=(
                    expected_field_eliminated_if_loss
                ),
                season_path_probability=season_probability,
                relative_season_value=relative_season_value,
                strategy_score=strategy_score,
            )
        )

    return sorted(
        scores,
        key=lambda item: item.strategy_score,
        reverse=True,
    )


def build_hidden_field_decision(
    week: int,
    current_week_games: List[NFLGame],
    paths: List[SurvivorPath],
    ownership_by_team: Dict[str, float],
    pool_size: int = DEFAULT_POOL_SIZE,
) -> HiddenFieldDecision:
    ranked = rank_hidden_field_options(
        week=week,
        current_week_games=current_week_games,
        paths=paths,
        ownership_by_team=ownership_by_team,
        pool_size=pool_size,
    )
    if not ranked:
        raise ValueError("No hidden-field Survivor options were generated.")

    primary = ranked[0]
    alternative = ranked[1] if len(ranked) > 1 else None

    if alternative is None:
        verdict = "LOCK"
        reason = "Only one viable strategic option was generated."
    else:
        score_gap = primary.strategy_score - alternative.strategy_score
        safety_gap = primary.win_probability - alternative.win_probability
        ownership_gap = (
            alternative.estimated_ownership - primary.estimated_ownership
        )

        if score_gap >= 0.025:
            verdict = "STRONG"
        elif score_gap >= 0.010:
            verdict = "LEAN"
        else:
            verdict = "TOSS-UP"

        if safety_gap >= 0.03:
            reason = (
                f"{primary.team}'s {safety_gap:.1%} survival edge outweighs "
                "the available ownership leverage."
            )
        elif ownership_gap >= 0.08:
            reason = (
                f"{primary.team} keeps comparable safety while projecting "
                f"{ownership_gap:.1%} lower ownership."
            )
        else:
            reason = (
                "The leading options are close after combining current-week "
                "safety, remaining-season value, and estimated ownership."
            )

    return HiddenFieldDecision(
        recommended_team=primary.team,
        alternative_team=alternative.team if alternative else None,
        recommended_score=primary,
        alternative_score=alternative,
        verdict=verdict,
        reason=reason,
    )


def build_hidden_field_report(
    decision: HiddenFieldDecision,
    pool_size: int = DEFAULT_POOL_SIZE,
) -> str:
    primary = decision.recommended_score
    lines = [
        "=== POOL-ADJUSTED SURVIVOR DECISION ===",
        "",
        f"Recommended pick: {decision.recommended_team}",
        f"Verdict: {decision.verdict}",
        f"Win probability: {primary.win_probability:.1%}",
        f"Estimated ownership: {primary.estimated_ownership:.1%}",
        (
            f"Expected entries on pick (pool {pool_size}): "
            f"{primary.expected_entries:.1f}"
        ),
        f"Reason: {decision.reason}",
    ]

    if decision.alternative_score is not None:
        alt = decision.alternative_score
        lines.extend(
            [
                "",
                f"Alternative: {alt.team}",
                f"Alternative win probability: {alt.win_probability:.1%}",
                f"Alternative estimated ownership: {alt.estimated_ownership:.1%}",
            ]
        )

    lines.extend(
        [
            "",
            "Ownership is modeled because PoolHost picks are hidden before lock.",
        ]
    )
    return "\n".join(lines)
