from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class DraftPlayer:
    name: str
    position: str
    team: str = ""
    rank: int = 999
    adp: float = 999.0
    tier: int = 99
    bye: int = 0
    position_rank: int = 99


POSITION_NEEDS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1}
POSITION_DEPTH = {"QB": 1, "RB": 4, "WR": 5, "TE": 2, "K": 1, "DST": 1}


def draft_score(player: DraftPlayer, roster_counts: Dict[str, int]) -> float:
    """Roster-aware draft score using rank, ADP, tier scarcity and positional need."""
    base = max(0.0, 1200.0 - float(player.rank) * 5.0)
    starter_need = max(0, POSITION_NEEDS.get(player.position, 0) - roster_counts.get(player.position, 0))
    depth_need = max(0, POSITION_DEPTH.get(player.position, 0) - roster_counts.get(player.position, 0))
    need_bonus = starter_need * 42.0 + depth_need * 8.0
    tier_bonus = max(0.0, 70.0 - float(player.tier) * 7.0)
    value_bonus = max(-60.0, min(60.0, (player.adp - player.rank) * 2.25))

    # Prevent early K/DST reaches unless the board is genuinely exhausted.
    late_position_penalty = 0.0
    if player.position in {"K", "DST"} and player.rank < 140:
        late_position_penalty = 120.0

    return base + need_bonus + tier_bonus + value_bonus - late_position_penalty


def rank_draft_board(players: List[DraftPlayer], roster_counts: Dict[str, int]) -> List[dict]:
    rows = []
    for player in players:
        score = draft_score(player, roster_counts)
        need = roster_counts.get(player.position, 0) < POSITION_NEEDS.get(player.position, 0)
        rows.append({**asdict(player), "draft_score": score, "roster_need": need})
    return sorted(rows, key=lambda row: row["draft_score"], reverse=True)


def roster_counts(roster: List[DraftPlayer]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for player in roster:
        counts[player.position] = counts.get(player.position, 0) + 1
    return counts
