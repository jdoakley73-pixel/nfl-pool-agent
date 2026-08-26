from dataclasses import dataclass
from typing import Dict, List, Set

from models import NFLGame


@dataclass
class SurvivorRecommendation:
    team: str
    opponent: str
    win_probability: float
    future_value: float
    survivor_score: float
    reason: str


def survivor_score(
    win_probability: float,
    future_value: float,
    future_weight: float = 0.20,
) -> float:
    """
    Higher is better.

    We want strong win probability now, while penalizing teams
    that may be especially valuable later in the season.
    """
    return win_probability - (future_value * future_weight)


def get_team_game_probability(
    game: NFLGame,
    team: str,
) -> tuple[float, str]:

    if game.home_win_prob is None or game.away_win_prob is None:
        raise ValueError("Game is missing win probabilities.")

    if team == game.home_team:
        return game.home_win_prob, game.away_team

    if team == game.away_team:
        return game.away_win_prob, game.home_team

    raise ValueError(f"{team} is not playing in this game.")


def recommend_survivor_pick(
    games: List[NFLGame],
    used_teams: Set[str],
    future_values: Dict[str, float] | None = None,
) -> List[SurvivorRecommendation]:

    if future_values is None:
        future_values = {}

    recommendations = []

    for game in games:
        for team in (game.home_team, game.away_team):

            if team in used_teams:
                continue

            probability, opponent = get_team_game_probability(
                game,
                team,
            )

            # Don't consider underdogs unless we later explicitly
            # add a contrarian survivor strategy.
            if probability < 0.50:
                continue

            future_value = future_values.get(team, 0.0)

            score = survivor_score(
                win_probability=probability,
                future_value=future_value,
            )

            reason = (
                f"{team} has a {probability:.1%} projected chance "
                f"to beat {opponent}. "
                f"Future-value penalty: {future_value:.2f}. "
                f"Survivor score: {score:.3f}."
            )

            recommendations.append(
                SurvivorRecommendation(
                    team=team,
                    opponent=opponent,
                    win_probability=probability,
                    future_value=future_value,
                    survivor_score=score,
                    reason=reason,
                )
            )

    return sorted(
        recommendations,
        key=lambda recommendation: recommendation.survivor_score,
        reverse=True,
    )
