def classify_decision_confidence(
    best_probability: float,
    second_probability: float,
) -> str:
    if second_probability <= 0:
        return "STRONG"

    relative_edge = (
        best_probability - second_probability
    ) / second_probability

    if relative_edge >= 0.05:
        return "STRONG"

    if relative_edge >= 0.02:
        return "LEAN"

    return "TOSS-UP"


def decision_confidence_reason(
    best_team: str,
    second_team: str,
    best_probability: float,
    second_probability: float,
) -> str:
    if second_probability <= 0:
        return (
            f"{best_team} has a clear advantage over "
            f"{second_team}."
        )

    relative_edge = (
        best_probability - second_probability
    ) / second_probability

    confidence = classify_decision_confidence(
        best_probability,
        second_probability,
    )

    if confidence == "TOSS-UP":
        return (
            f"{best_team} is currently preferred over "
            f"{second_team}, but the projected strategic "
            f"advantage is only {relative_edge:.2%}. "
            f"Either choice is defensible."
        )

    if confidence == "LEAN":
        return (
            f"{best_team} holds a modest "
            f"{relative_edge:.2%} strategic advantage over "
            f"{second_team}."
        )

    return (
        f"{best_team} holds a meaningful "
        f"{relative_edge:.2%} strategic advantage over "
        f"{second_team}."
    )
