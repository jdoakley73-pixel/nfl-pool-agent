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


POSITION_NEEDS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1}


def draft_score(player: DraftPlayer, roster_counts: Dict[str, int]) -> float:
    """Simple manual-mode draft score until a live fantasy data feed is connected."""
    base = max(0.0, 1000.0 - float(player.rank) * 5.0)
    need = max(0, POSITION_NEEDS.get(player.position, 0) - roster_counts.get(player.position, 0))
    need_bonus = need * 30.0
    tier_bonus = max(0.0, 50.0 - float(player.tier) * 5.0)
    value_bonus = max(-50.0, min(50.0, (player.adp - player.rank) * 2.0))
    return base + need_bonus + tier_bonus + value_bonus


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
