from html import unescape
from io import StringIO
import re
from typing import Iterable, List

import pandas as pd
import requests

from fantasy_gm import DraftPlayer


RANKING_URLS = {
    "PPR": [
        "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php?export=xls",
        "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php",
        "https://www.fantasypros.com/nfl/cheatsheets/top-ppr-players.php",
    ],
    "Half PPR": [
        "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php?export=xls",
        "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php",
        "https://www.fantasypros.com/nfl/cheatsheets/top-half-ppr-players.php",
        "https://sports.yahoo.com/fantasy/article/fantasy-football-rankings-half-ppr-2026-160643679.html",
    ],
    "Standard": [
        "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php?export=xls",
        "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php",
        "https://www.fantasypros.com/nfl/cheatsheets/top-players.php",
    ],
}

# This is intentionally small: it is not meant to replace the live board. It guarantees
# the war room never opens completely empty if every external rankings site is unavailable.
EMERGENCY_HALF_PPR = [
    ("Jahmyr Gibbs", "RB", "DET"),
    ("Bijan Robinson", "RB", "ATL"),
    ("Ja'Marr Chase", "WR", "CIN"),
    ("Puka Nacua", "WR", "LAR"),
    ("Jaxon Smith-Njigba", "WR", "SEA"),
    ("Amon-Ra St. Brown", "WR", "DET"),
    ("Jonathan Taylor", "RB", "IND"),
    ("Christian McCaffrey", "RB", "SF"),
    ("James Cook III", "RB", "BUF"),
    ("CeeDee Lamb", "WR", "DAL"),
    ("Justin Jefferson", "WR", "MIN"),
    ("Chase Brown", "RB", "CIN"),
    ("Saquon Barkley", "RB", "PHI"),
    ("A.J. Brown", "WR", "NE"),
    ("Drake London", "WR", "ATL"),
    ("De'Von Achane", "RB", "MIA"),
    ("Nico Collins", "WR", "HOU"),
    ("Omarion Hampton", "RB", "LAC"),
    ("Kenneth Walker III", "RB", "KC"),
    ("Brock Bowers", "TE", "LV"),
    ("Derrick Henry", "RB", "BAL"),
    ("George Pickens", "WR", "DAL"),
    ("Ashton Jeanty", "RB", "LV"),
    ("Chris Olave", "WR", "NO"),
    ("Trey McBride", "TE", "ARI"),
    ("Josh Allen", "QB", "BUF"),
    ("Lamar Jackson", "QB", "BAL"),
    ("Drake Maye", "QB", "NE"),
    ("Joe Burrow", "QB", "CIN"),
    ("Jayden Daniels", "QB", "WAS"),
    ("Jalen Hurts", "QB", "PHI"),
    ("Caleb Williams", "QB", "CHI"),
    ("Justin Herbert", "QB", "LAC"),
    ("Trevor Lawrence", "QB", "JAC"),
    ("Dak Prescott", "QB", "DAL"),
    ("Brock Purdy", "QB", "SF"),
    ("Colston Loveland", "TE", "CHI"),
    ("Tyler Warren", "TE", "IND"),
    ("Tucker Kraft", "TE", "GB"),
    ("Sam LaPorta", "TE", "DET"),
    ("Harold Fannin Jr.", "TE", "CLE"),
    ("Kyle Pitts Sr.", "TE", "ATL"),
    ("George Kittle", "TE", "SF"),
    ("Travis Kelce", "TE", "KC"),
    ("Dalton Kincaid", "TE", "BUF"),
]


def _position_parts(value: str):
    text = str(value).strip().upper().replace("D/ST", "DST")
    match = re.match(r"([A-Z]+)(\d+)?", text)
    if not match:
        return text, 99
    return match.group(1), int(match.group(2) or 99)


def _player_parts(value: str):
    text = re.sub(r"\s+", " ", str(value)).strip()
    match = re.match(r"(.+?)\s*\(([A-Z]{2,3})\)\s*$", text)
    if match:
        return match.group(1).strip(), match.group(2)
    return text, ""


def _safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _safe_float(value, default=999.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _make_player(name: str, position: str, team: str, rank: int, adp=None, bye=0, position_rank=99):
    position = position.upper().replace("D/ST", "DST")
    tier_size = 6 if position in {"RB", "WR"} else 4
    if position_rank == 99:
        position_rank = rank
    tier = ((max(position_rank, 1) - 1) // tier_size) + 1
    return DraftPlayer(
        name=name.strip(),
        position=position,
        team=team.strip().upper(),
        rank=int(rank),
        adp=float(rank if adp is None else adp),
        tier=int(tier),
        bye=int(bye or 0),
        position_rank=int(position_rank),
    )


def parse_rankings_html(html: str, limit: int = 300) -> List[DraftPlayer]:
    """Parse rankings tables from FantasyPros/Yahoo-style pages."""
    tables = pd.read_html(StringIO(html))
    best_players: List[DraftPlayer] = []

    for table in tables:
        columns = [str(col).upper().strip() for col in table.columns]
        normalized = {str(col).upper().strip(): col for col in table.columns}
        rank_col = next((col for key, col in normalized.items() if key in {"RK", "RANK"} or key.startswith("RANK")), None)
        player_col = next((col for key, col in normalized.items() if "PLAYER" in key), None)
        if rank_col is None or player_col is None:
            continue

        pos_col = next((col for key, col in normalized.items() if key.startswith("POS")), None)
        bye_col = next((col for key, col in normalized.items() if "BYE" in key), None)
        adp_col = next((col for key, col in normalized.items() if key == "ADP" or key.endswith(" ADP")), None)
        rows: List[DraftPlayer] = []

        for _, row in table.iterrows():
            rank = _safe_int(row[rank_col], 0)
            if rank < 1 or rank > limit:
                continue

            raw_player = str(row[player_col])
            name, team = _player_parts(raw_player)
            raw_pos = str(row[pos_col]) if pos_col is not None else ""

            # Some tables render "Player Name" as "Name (TEAM) POS - TEAM".
            if not raw_pos:
                pos_match = re.search(r"\b(QB|RB|WR|TE|K|DST|D/ST)\s*[- ]\s*([A-Z]{2,3})\b", raw_player.upper())
                if pos_match:
                    raw_pos = pos_match.group(1)
                    team = team or pos_match.group(2)
                    name = re.sub(r"\s+\b(?:QB|RB|WR|TE|K|DST|D/ST)\s*[- ]\s*[A-Z]{2,3}\b.*$", "", name, flags=re.I).strip()

            position, position_rank = _position_parts(raw_pos)
            if position not in {"QB", "RB", "WR", "TE", "K", "DST"}:
                continue

            bye = _safe_int(row[bye_col], 0) if bye_col is not None and pd.notna(row[bye_col]) else 0
            adp = _safe_float(row[adp_col], float(rank)) if adp_col is not None and pd.notna(row[adp_col]) else float(rank)
            rows.append(_make_player(name, position, team, rank, adp=adp, bye=bye, position_rank=position_rank))

        if len(rows) > len(best_players):
            best_players = rows

    if not best_players:
        raise RuntimeError("No usable rankings table found.")
    return best_players[:limit]


def parse_ranked_list_html(html: str, limit: int = 300) -> List[DraftPlayer]:
    """Fallback parser for simple cheat-sheet lists such as '1. Player RB-TEAM'."""
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"\s+", " ", text)
    pattern = re.compile(
        r"(?:^|\s)(\d{1,3})\.\s+([A-Za-zÀ-ÖØ-öø-ÿ0-9.'’\- ]{2,45}?)\s+(QB|RB|WR|TE|K|DST|D/ST)\s*[-–]\s*([A-Z]{2,3})\b",
        re.I,
    )
    matches = pattern.findall(text)
    players: List[DraftPlayer] = []
    seen = set()
    position_counts = {}

    for rank_text, name, position, team in matches:
        rank = int(rank_text)
        if rank > limit:
            continue
        key = (name.strip().lower(), position.upper())
        if key in seen:
            continue
        seen.add(key)
        pos = position.upper().replace("D/ST", "DST")
        position_counts[pos] = position_counts.get(pos, 0) + 1
        players.append(
            _make_player(
                name=name.strip(),
                position=pos,
                team=team,
                rank=rank,
                adp=float(rank),
                position_rank=position_counts[pos],
            )
        )

    players.sort(key=lambda p: p.rank)
    if not players:
        raise RuntimeError("No ranked-list players found.")
    return players[:limit]


def _dedupe(players: Iterable[DraftPlayer], limit: int) -> List[DraftPlayer]:
    result = []
    seen = set()
    for player in sorted(players, key=lambda p: p.rank):
        key = (player.name.lower(), player.position)
        if key in seen:
            continue
        seen.add(key)
        result.append(player)
        if len(result) >= limit:
            break
    return result


def emergency_rankings(limit: int = 300) -> List[DraftPlayer]:
    counts = {}
    rows = []
    for rank, (name, position, team) in enumerate(EMERGENCY_HALF_PPR, start=1):
        counts[position] = counts.get(position, 0) + 1
        rows.append(_make_player(name, position, team, rank, adp=float(rank), position_rank=counts[position]))
    return rows[:limit]


def fetch_live_rankings(scoring: str = "PPR", limit: int = 300) -> List[DraftPlayer]:
    """Fetch a draft board with multiple live fallbacks and a non-empty emergency board."""
    urls = RANKING_URLS.get(scoring, RANKING_URLS["PPR"])
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }
    errors = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text

            for parser in (parse_rankings_html, parse_ranked_list_html):
                try:
                    players = _dedupe(parser(html, limit=limit), limit)
                    # A live source is only considered draft-ready if it has meaningful depth.
                    if len(players) >= 24:
                        return players
                except Exception as parse_exc:
                    errors.append(f"{url} / {parser.__name__}: {parse_exc}")
        except Exception as request_exc:
            errors.append(f"{url}: {request_exc}")

    # Never return an empty list on draft night. The UI identifies this as emergency mode.
    return emergency_rankings(limit=limit)
