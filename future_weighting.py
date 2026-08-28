"""
Future uncertainty weighting for Survivor planning.

Early-season market probabilities deserve more confidence than
projections many weeks into the future. This module gradually
pulls distant win probabilities toward 50/50.

Example:
    A Week 1 team projected at 80% remains near 80%.
    A Week 18 team projected at 80% is discounted because that
    estimate is much less certain months in advance.
"""


def future_confidence(
    target_week: int,
    current_week: int = 1,
    decay_per_week: float = 0.035,
    minimum_confidence: float = 0.45,
) -> float:
    """
    Return confidence in a projected win probability.

    Confidence declines as the target week gets farther from
    the current decision week.
    """
    weeks_ahead = max(0, target_week - current_week)

    confidence = 1.0 - (weeks_ahead * decay_per_week)

    return max(minimum_confidence, confidence)


def uncertainty_adjusted_probability(
    win_probability: float,
    target_week: int,
    current_week: int = 1,
    decay_per_week: float = 0.035,
    minimum_confidence: float = 0.45,
) -> float:
    """
    Pull distant projections toward 50%.

    win_probability should be expressed from 0.0 to 1.0.
    """
    confidence = future_confidence(
        target_week=target_week,
        current_week=current_week,
        decay_per_week=decay_per_week,
        minimum_confidence=minimum_confidence,
    )

    return 0.50 + ((win_probability - 0.50) * confidence)


def future_value_weight(
    target_week: int,
    current_week: int = 1,
) -> float:
    """
    Weight used when deciding how strongly to preserve a team
    for a future week.

    Near future matters heavily.
    Far future still matters, but increasingly represents
   
