from io import StringIO
import re
from typing import List

import pandas as pd
import requests

from fantasy_gm import DraftPlayer


RANKING_URLS = {
    "PPR": "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php",
    "Half PPR": "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php",
    "Standard": "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php",
}


def _position_parts(value: str):
    match = re.match(r"([A-Z]+)(\d+)?", str(value).strip().upper())
    if not match:
        return str(value).strip().upper(), 99
    return match.group(1), int(match.group(2) or 99)


def _player_parts(value: str):
    text = re.sub(r"\s+", " ", str(value)).strip()
    match = re.match(r"(.+?)\s*\(([A-Z]{2,3})\)\s*$", text)
    if match:
        return match.group(1).strip(), match.group(2)
    return text, ""


def parse_rankings_html(html: str, limit: int = 300) -> List[DraftPlayer]:
    tables = pd.read_html(StringIO(html))
    target = None
    for table in tables:
        columns = [str(col).upper() for col in table.columns]
        if any("RK" == col or "RANK" in col for col in columns) and any("PLAYER" in col for col in columns):
            target = table
            break
    if target is None:
        raise RuntimeError("Could not locate fantasy rankings table.")

    normalized = {str(col).upper(): col for col in target.columns}
    rank_col = next(col for key, col in normalized.items() if key == "RK" or "RANK" in key)
    player_col = next(col for key, col in normalized.items() if "PLAYER" in key)
    pos_col = next((col for key, col in normalized.items() if key.startswith("POS")), None)
    bye_col = next((col for key, col in normalized.items() if "BYE" in key), None)
    adp_col = next((col for key, col in normalized.items() if key == "ADP"), None)

    players = []
    for _, row in target.iterrows():
        try:
            rank = int(float(row[rank_col]))
        except (TypeError, ValueError):
            continue
        if rank > limit:
            continue

        name, team = _player_parts(row[player_col])
        position, position_rank = _position_parts(row[pos_col] if pos_col else "")
        try:
            bye = int(float(row[bye_col])) if bye_col is not None and pd.notna(row[bye_col]) else 0
        except (TypeError, ValueError):
            bye = 0
        try:
            adp = float(row[adp_col]) if adp_col is not None and pd.notna(row[adp_col]) else float(rank)
        except (TypeError, ValueError):
            adp = float(rank)

        tier_size = 6 if position in {"RB", "WR"} else 4
        tier = ((max(position_rank, 1) - 1) // tier_size) + 1
        players.append(
            DraftPlayer(
                name=name,
                position=position,
                team=team,
                rank=rank,
                adp=adp,
                tier=tier,
                bye=bye,
                position_rank=position_rank,
            )
        )

    if not players:
        raise RuntimeError("Fantasy rankings table returned no usable players.")
    return players


def fetch_live_rankings(scoring: str = "PPR", limit: int = 300) -> List[DraftPlayer]:
    url = RANKING_URLS.get(scoring, RANKING_URLS["PPR"])
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 FootballCommandCenter/1.0"},
        timeout=20,
    )
    response.raise_for_status()
    return parse_rankings_html(response.text, limit=limit)
