from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from future_weighting import uncertainty_adjusted_probability
from models import NFLGame


@dataclass
class SurvivorPath:
    picks: Dict[int, str]
    survival_probability: float


def team_probability(
    game: NFLGame,
    team: str,
) -> float:
    if game.home_win_prob is None or game.away_win_prob is None:
        raise ValueError("Game is missing win probabilities.")

    if team == game.home_team:
        return game.home_win_prob

    if team == game.away_team:
        return game.away_win_prob

    raise ValueError(f"{team} is not playing in this game.")


def group_games_by_week(
    games: List[NFLGame],
) -> Dict[int, List[NFLGame]]:
    grouped: Dict[int, List[NFLGame]] = {}

    for game in games:
        grouped.setdefault(game.week, []).append(game)

    return grouped


def available_week_choices(
    games: List[NFLGame],
    used_teams: Set[str],
    minimum_probability: float = 0.50,
    current_week: int = 1,
) -> List[Tuple[str, float]]:
    choices: List[Tuple[str, float]] = []

    for game in games:
        for team in (game.home_team, game.away_team):
            if team in used_teams:
                continue

            raw_probability = team_probability(
                game,
                team,
            )

            probability = uncertainty_adjusted_probability(
                win_probability=raw_probability,
                target_week=game.week,
                current_week=current_week,
            )

            if probability < minimum_probability:
                continue

            choices.append(
                (
                    team,
                    probability,
                )
            )

    return sorted(
        choices,
        key=lambda item: item[1],
        reverse=True,
    )


def search_survivor_paths(
    games: List[NFLGame],
    start_week: int,
    end_week: int,
    used_teams: Set[str] | None = None,
    minimum_probability: float = 0.50,
    beam_width: int = 500,
) -> List[SurvivorPath]:
    """
    Search for strong Survivor paths across multiple weeks.

    Survival probability is the product of each week's
    projected win probability.

    beam_width prevents the number of candidate paths
    from exploding as the horizon gets longer.
    """

    if used_teams is None:
        used_teams = set()

    games_by_week = group_games_by_week(games)

    paths = [
        SurvivorPath(
            picks={},
            survival_probability=1.0,
        )
    ]

    for week in range(
        start_week,
        end_week + 1,
    ):
        week_games = games_by_week.get(
            week,
            [],
        )

        if not week_games:
            continue

        new_paths: List[SurvivorPath] = []

        for path in paths:
            path_used_teams = (
                set(path.picks.values())
                | used_teams
            )

            choices = available_week_choices(
                games=week_games,
                used_teams=path_used_teams,
                minimum_probability=minimum_probability,
                current_week=start_week,
            )

            choices = choices[:12]

            for team, probability in choices:
                picks = dict(path.picks)
                picks[week] = team

                new_paths.append(
                    SurvivorPath(
                        picks=picks,
                        survival_probability=(
                            path.survival_probability
                            * probability
                        ),
                    )
                )

        if not new_paths:
            break

        paths = sorted(
            new_paths,
            key=lambda path: (
                path.survival_probability
            ),
            reverse=True,
        )[:beam_width]

    return paths


def best_survivor_paths(
    games: List[NFLGame],
    start_week: int,
    end_week: int,
    used_teams: Set[str] | None = None,
    top_n: int = 10,
) -> List[SurvivorPath]:
    paths = search_survivor_paths(
        games=games,
        start_week=start_week,
        end_week=end_week,
        used_teams=used_teams,
    )

    return paths[:top_n]
