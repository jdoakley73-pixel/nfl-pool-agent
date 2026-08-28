def future_confidence(
    target_week: int,
    current_week: int = 1,
    decay_per_week: float = 0.035,
    minimum_confidence: float = 0.45,
) -> float:
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
    weeks_ahead = max(0, target_week - current_week)

    if weeks_ahead <= 2:
        return 1.00
    elif weeks_ahead <= 7:
        return 0.85
    elif weeks_ahead <= 12:
        return 0.65
    else:
        return 0.45
