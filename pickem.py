from dataclasses import dataclass
from typing import List

from models import NFLGame


@dataclass
class PickemRecommendation:
    matchup: str
    pick: str
    win_probability: float
    confidence: str
    leverage_flag: bool
    reason: str


def confidence_label(probability: float) -> str:
    if probability >= 0.80:
        return "LOCK"
    if probability >= 0.70:
        return "HIGH"
    if probability >= 0.60:
        return "MEDIUM"
    return "LOW"


def recommend_pick(
    game: NFLGame,
    public_pick_pct: float | None = None,
) -> PickemRecommendation:

    if game.home_win_prob is None or game.away_win_prob is None:
        raise ValueError("Game is missing win probabilities.")

    if game.home_win_prob >= game.away_win_prob:
        pick = game.home_team
        probability = game.home_win_prob
    else:
        pick = game.away_team
        probability = game.away_win_prob

    leverage_flag = False
    reason_parts = [
        f"{pick} has the higher projected win probability "
        f"({probability:.1%})."
    ]

    if public_pick_pct is not None:
        edge = probability - public_pick_pct

        if probability >= 0.55 and edge >= 0.10:
            leverage_flag = True
            reason_parts.append(
                f"Possible pool leverage: projected win probability "
                f"exceeds public selection rate by {edge:.1%}."
            )

    return PickemRecommendation(
        matchup=f"{game.away_team} @ {game.home_team}",
        pick=pick,
        win_probability=probability,
        confidence=confidence_label(probability),
        leverage_flag=leverage_flag,
        reason=" ".join(reason_parts),
    )


def build_pickem_card(
    games: List[NFLGame],
) -> List[PickemRecommendation]:

    recommendations = []

    for game in games:
        recommendations.append(recommend_pick(game))

    return sorted(
        recommendations,
        key=lambda recommendation: recommendation.win_probability,
        reverse=True,
    )
