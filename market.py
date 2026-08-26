from typing import List

from models import NFLGame
from odds import remove_vig


def apply_market_probabilities(game: NFLGame) -> NFLGame:
    """
    Convert a game's moneylines into no-vig market
    win probabilities and store them on the game.
    """

    if (
        game.home_moneyline is None
        or game.away_moneyline is None
    ):
        raise ValueError(
            f"Missing moneyline for "
            f"{game.away_team} @ {game.home_team}"
        )

    home_probability, away_probability = remove_vig(
        home_moneyline=game.home_moneyline,
        away_moneyline=game.away_moneyline,
    )

    game.home_win_prob = home_probability
    game.away_win_prob = away_probability

    return game


def apply_market_to_games(
    games: List[NFLGame],
) -> List[NFLGame]:
    """
    Apply no-vig market probabilities to every game.
    """

    processed_games = []

    for game in games:
        processed_games.append(
            apply_market_probabilities(game)
        )

    return processed_games


def validate_probabilities(game: NFLGame) -> bool:
    """
    Confirm probabilities exist and approximately sum to 100%.
    """

    if (
        game.home_win_prob is None
        or game.away_win_prob is None
    ):
        return False

    total = game.home_win_prob + game.away_win_prob

    return abs(total - 1.0) < 0.0001
