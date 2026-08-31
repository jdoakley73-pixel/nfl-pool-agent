from typing import Dict, List, Sequence


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


def _market_pick(player) -> float:
    """Blend expert rank and ADP so the attack map is useful even when one source is noisy."""
    rank = float(getattr(player, "rank", 999) or 999)
    adp = float(getattr(player, "adp", rank) or rank)
    if adp >= 900:
        return rank
    return (rank * 0.55) + (adp * 0.45)


def _label(player) -> str:
    position = getattr(player, "position", "")
    position_rank = getattr(player, "position_rank", 99)
    name = getattr(player, "name", "Unknown")
    suffix = f" {position}{position_rank}" if position else ""
    return f"{name}{suffix}"


def build_pick_target_tiers(
    players: Sequence[object],
    draft_slot: int,
    team_count: int = 12,
    rounds: int = 10,
    names_per_tier: int = 4,
) -> List[Dict[str, object]]:
    """Build live player-name target bands around each of the user's snake picks.

    Bands are based on a blended expert-rank/ADP market pick:
    - dream_fall: normally gone before our pick, but an instant value if available
    - core_targets: priced directly around our selection
    - next_turn_risk: players likely to be gone before our following selection
    - reach_ceiling: furthest range we should consider without a special roster reason
    """
    ordered = sorted(players, key=_market_pick)
    user_picks = [snake_pick_for_round(r, draft_slot, team_count) for r in range(1, rounds + 1)]
    rows: List[Dict[str, object]] = []

    for idx, overall_pick in enumerate(user_picks):
        round_number = idx + 1
        next_pick = user_picks[idx + 1] if idx + 1 < len(user_picks) else overall_pick + team_count

        dream_low = max(1.0, overall_pick - 12.0)
        dream_high = max(1.0, overall_pick - 4.0)
        core_low = max(1.0, overall_pick - 3.0)
        core_high = overall_pick + 6.0
        risk_low = overall_pick + 6.0
        risk_high = min(float(next_pick - 1), overall_pick + 16.0)
        reach_high = overall_pick + 12.0

        dream = [p for p in ordered if dream_low <= _market_pick(p) <= dream_high][:names_per_tier]
        core = [p for p in ordered if core_low <= _market_pick(p) <= core_high][:names_per_tier]
        risk = [p for p in ordered if risk_low < _market_pick(p) <= risk_high][:names_per_tier]

        reach_candidates = [p for p in ordered if core_high < _market_pick(p) <= reach_high]
        reach_line = reach_candidates[-1] if reach_candidates else None

        rows.append(
            {
                "round": round_number,
                "overall_pick": overall_pick,
                "dream_fall": [_label(p) for p in dream],
                "core_targets": [_label(p) for p in core],
                "next_turn_risk": [_label(p) for p in risk],
                "reach_ceiling": _label(reach_line) if reach_line else "Hold the line",
            }
        )

    return rows


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
