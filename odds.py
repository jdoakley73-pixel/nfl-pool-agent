from dataclasses import dataclass


@dataclass
class MarketProbability:
    team: str
    moneyline: int
    implied_probability: float


def moneyline_to_probability(moneyline: int) -> float:
    """
    Convert American moneyline odds to raw implied probability.

    Examples:
    -200 -> 66.7%
    +150 -> 40.0%
    """

    if moneyline < 0:
        return abs(moneyline) / (abs(moneyline) + 100)

    return 100 / (moneyline + 100)


def remove_vig(
    home_moneyline: int,
    away_moneyline: int,
) -> tuple[float, float]:
    """
    Convert both moneylines into no-vig win probabilities.

    Returns:
        (home_probability, away_probability)
    """

    home_raw = moneyline_to_probability(home_moneyline)
    away_raw = moneyline_to_probability(away_moneyline)

    total = home_raw + away_raw

    if total == 0:
        raise ValueError("Invalid moneyline probabilities.")

    home_probability = home_raw / total
    away_probability = away_raw / total

    return home_probability, away_probability


def market_edge(
    model_probability: float,
    market_probability: float,
) -> float:
    """
    Difference between our projected probability
    and the no-vig market probability.

    Positive = our model likes the team more than the market.
    Negative = our model likes the team less than the market.
    """

    return model_probability - market_probability


def format_probability(probability: float) -> str:
    return f"{probability:.1%}"
