from dataclasses import dataclass
from typing import Dict, List

from models import NFLGame


@dataclass
class OwnershipEstimate:
    team: str
    win_probability: float
    estimated_ownership: float
    raw_popularity_score: float


def favorite_for_game(game: NFLGame):
    if game.home_win_prob >= game.away_win_prob:
        return (
            game.home_team,
            game.home_win_prob,
            True,
        )

    return (
        game.away_team,
        game.away_win_prob,
        False,
    )


def popularity_score(
    win_probability: float,
    is_home: bool,
) -> float:
    """
    Estimate how attractive a team will look to a typical
    Survivor player.

    This is intentionally a heuristic. It is NOT actual
    PoolHost ownership data.
    """

    # Survivor players disproportionately gravitate toward
    # large favorites, so make probability nonlinear.
    score = win_probability ** 5

    # Small home-favorite bump.
    if is_home:
        score *= 1.08

    # Very obvious favorites attract additional public picks.
    if win_probability >= 0.80:
        score *= 1.30
    elif win_probability >= 0.75:
        score *= 1.15
    elif win_probability >= 0.70:
        score *= 1.05

    return score


def estimate_survivor_ownership(
    games: List[NFLGame],
    used_teams=None,
) -> List[OwnershipEstimate]:
    if used_teams is None:
        used_teams = set()
    else:
        used_teams = set(used_teams)

    candidates = []

    for game in games:
        team, win_probability, is_home = favorite_for_game(
            game
        )

        if team in used_teams:
            continue

        # Avoid treating marginal favorites as serious
        # public Survivor candidates.
        if win_probability < 0.55:
            continue

        score = popularity_score(
            win_probability=win_probability,
            is_home=is_home,
        )

        candidates.append(
            (
                team,
                win_probability,
                score,
            )
        )

    total_score = sum(
        candidate[2]
        for candidate in candidates
    )

    if total_score <= 0:
        return []

    estimates = []

    for team, win_probability, score in candidates:
        ownership = score / total_score

        estimates.append(
            OwnershipEstimate(
                team=team,
                win_probability=win_probability,
                estimated_ownership=ownership,
                raw_popularity_score=score,
            )
        )

    return sorted(
        estimates,
        key=lambda item: item.estimated_ownership,
        reverse=True,
    )


def ownership_dict(
    estimates: List[OwnershipEstimate],
) -> Dict[str, float]:
    return {
        estimate.team: estimate.estimated_ownership
        for estimate in estimates
    }


def build_ownership_report(
    estimates: List[OwnershipEstimate],
) -> str:
    lines = [
        "=== ESTIMATED SURVIVOR OWNERSHIP ===",
        "",
    ]

    for rank, estimate in enumerate(
        estimates,
        start=1,
    ):
        lines.append(
            f"{rank}. {estimate.team}: "
            f"{estimate.estimated_ownership:.1%} "
            f"| Win: {estimate.win_probability:.1%}"
        )

    return "\n".join(lines)
