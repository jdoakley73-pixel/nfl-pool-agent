from dataclasses import dataclass
from datetime import datetime
from typing import List

from models import NFLGame


@dataclass
class RawGameData:
    week: int
    kickoff: datetime
    away_team: str
    home_team: str

    away_moneyline: int | None = None
    home_moneyline: int | None = None

    spread: float | None = None
    total: float | None = None


def build_game_from_raw(raw: RawGameData) -> NFLGame:
    """
    Convert provider data into the common NFLGame model.

    Win probabilities are intentionally left blank here.
    They will be calculated from market/model inputs elsewhere.
    """

    return NFLGame(
        week=raw.week,
        kickoff=raw.kickoff,
        away_team=raw.away_team,
        home_team=raw.home_team,
        away_moneyline=raw.away_moneyline,
        home_moneyline=raw.home_moneyline,
        spread=raw.spread,
        total=raw.total,
    )


def normalize_team_name(team: str) -> str:
    """
    Convert common team names into a consistent abbreviation.
    """

    aliases = {
        "Arizona Cardinals": "ARI",
        "Atlanta Falcons": "ATL",
        "Baltimore Ravens": "BAL",
        "Buffalo Bills": "BUF",
        "Carolina Panthers": "CAR",
        "Chicago Bears": "CHI",
        "Cincinnati Bengals": "CIN",
        "Cleveland Browns": "CLE",
        "Dallas Cowboys": "DAL",
        "Denver Broncos": "DEN",
        "Detroit Lions": "DET",
        "Green Bay Packers": "GB",
        "Houston Texans": "HOU",
        "Indianapolis Colts": "IND",
        "Jacksonville Jaguars": "JAX",
        "Kansas City Chiefs": "KC",
        "Las Vegas Raiders": "LV",
        "Los Angeles Chargers": "LAC",
        "Los Angeles Rams": "LAR",
        "Miami Dolphins": "MIA",
        "Minnesota Vikings": "MIN",
        "New England Patriots": "NE",
        "New Orleans Saints": "NO",
        "New York Giants": "NYG",
        "New York Jets": "NYJ",
        "Philadelphia Eagles": "PHI",
        "Pittsburgh Steelers": "PIT",
        "San Francisco 49ers": "SF",
        "Seattle Seahawks": "SEA",
        "Tampa Bay Buccaneers": "TB",
        "Tennessee Titans": "TEN",
        "Washington Commanders": "WAS",
    }

    cleaned = team.strip()

    return aliases.get(cleaned, cleaned)


def build_games(
    raw_games: List[RawGameData],
) -> List[NFLGame]:
    """
    Normalize provider data into NFLGame objects.
    """

    games = []

    for raw in raw_games:
        normalized = RawGameData(
            week=raw.week,
            kickoff=raw.kickoff,
            away_team=normalize_team_name(raw.away_team),
            home_team=normalize_team_name(raw.home_team),
            away_moneyline=raw.away_moneyline,
            home_moneyline=raw.home_moneyline,
            spread=raw.spread,
            total=raw.total,
        )

        games.append(build_game_from_raw(normalized))

    return games
