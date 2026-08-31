from typing import Dict, Iterable, List, Sequence


def snake_pick_for_round(round_number: int, draft_slot: int, team_count: int = 12) -> int:
    """Return the overall pick number for a snake-draft slot in a given round."""
    if round_number < 1:
        raise ValueError("round_number must be >= 1")
    if draft_slot < 1 or draft_slot > team_count:
        raise ValueError("draft_slot must be within the league size")

    round_start = (round_number - 1) * team_count
    if round_number % 2 == 1:
        return round_start + draft_slot
    return round_start + (team_count - draft_slot + 1)


def snake_attack_map(draft_slot: int, team_count: int = 12, rounds: int = 10) -> List[Dict[str, int]]:
    rows: List[Dict[str, int]] = []
    for round_number in range(1, rounds + 1):
        rows.append(
            {
                "round": round_number,
                "overall_pick": snake_pick_for_round(round_number, draft_slot, team_count),
            }
        )
    return rows


def upcoming_user_picks(
    current_overall_pick: int,
    draft_slot: int,
    team_count: int = 12,
    rounds: int = 18,
    limit: int = 4,
) -> List[int]:
    picks = [
        snake_pick_for_round(round_number, draft_slot, team_count)
        for round_number in range(1, rounds + 1)
    ]
    return [pick for pick in picks if pick >= current_overall_pick][:limit]


def turn_partner_pick(overall_pick: int, draft_slot: int, team_count: int = 12, rounds: int = 18) -> int | None:
    picks = [
        snake_pick_for_round(round_number, draft_slot, team_count)
        for round_number in range(1, rounds + 1)
    ]
    if overall_pick not in picks:
        return None
    idx = picks.index(overall_pick)
    if idx + 1 < len(picks):
        return picks[idx + 1]
    return None


def build_turn_recommendations(board: Sequence[dict], roster_counts: Dict[str, int], limit: int = 8) -> Dict[str, object]:
    """Build concise two-pick turn advice from the already-ranked draft board.

    The first choice is pure best-current-value. The second choice favors a different
    position when the scores are close so the drafter can exploit the short turn
    without forcing roster construction.
    """
    candidates = list(board[: max(limit, 2)])
    if not candidates:
        return {"take": None, "backup": None, "pair": None, "avoid_reach": None}

    take = candidates[0]
    backup = candidates[1] if len(candidates) > 1 else None

    pair = None
    for candidate in candidates[1:]:
        score_gap = float(take["draft_score"]) - float(candidate["draft_score"])
        if candidate["position"] != take["position"] and score_gap <= 85:
            pair = candidate
            break
    if pair is None:
        pair = backup

    avoid_reach = None
    for candidate in reversed(candidates):
        if candidate["position"] in {"QB", "TE"} and roster_counts.get(candidate["position"], 0) == 0:
            if float(take["draft_score"]) - float(candidate["draft_score"]) > 55:
                avoid_reach = candidate
                break

    return {
        "take": take,
        "backup": backup,
        "pair": pair,
        "avoid_reach": avoid_reach,
    }
