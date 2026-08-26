from collections import defaultdict
from typing import Dict, List

from models import NFLGame


def team_probability(game: NFLGame, team: str) -> float:
    """Return a team's projected win probability for a game."""

    if game.home_win_prob is None or game.away_win_prob is None:
        raise ValueError("Game is missing win probabilities.")

    if team == game.home_team:
        return game.home_win_prob

    if team == game.away_team:
        return game.away_win_prob

    raise ValueError(f"{team} is not playing in this game.")


def calculate_future_values(
    future_games: List[NFLGame],
    current_week: int,
    premium_threshold: float = 0.70,
) -> Dict[str, float]:
    """
    Estimate how valuable each NFL team may be later in Survivor.

    Teams receive future value for favorable upcoming matchups.
    Bigger favorites and nearer-term premium opportunities receive
    more weight.
    """

    values = defaultdict(float)

    for game in future_games:

        if game.week <= current_week:
            continue

        weeks_away = game.week - current_week

        # Nearer opportunities are somewhat more valuable because
        # projections become less certain farther into the future.
        time_weight = 1 / weeks_away

        for team in (game.home_team, game.away_team):

            probability = team_probability(game, team)

            if probability < premium_threshold:
                continue

            # Only count the portion above our premium threshold.
            matchup_value = probability - premium_threshold

            values[team] += matchup_value * time_weight

    return dict(values)


def rank_future_team_value(
    future_values: Dict[str, float],
) -> List[tuple[str, float]]:
    """Rank teams from most valuable to preserve to least."""

    return sorted(
        future_values.items(),
        key=lambda item: item[1],
        reverse=True,
    )
