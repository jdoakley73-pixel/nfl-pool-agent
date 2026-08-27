from datetime import datetime
from typing import List

import requests

from data_provider import RawGameData


ESPN_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/"
    "sports/football/nfl/scoreboard"
)


def fetch_nfl_week(
    season: int,
    week: int,
) -> List[RawGameData]:
    """
    Fetch an NFL regular-season week from ESPN's scoreboard feed.

    This provides schedule/game information only.
    Betting odds will be added by a separate provider.
    """

    params = {
        "dates": season,
        "seasontype": 2,
        "week": week,
        "limit": 100,
    }

    response = requests.get(
        ESPN_SCOREBOARD_URL,
        params=params,
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()

    games = []

    for event in payload.get("events", []):
        competitions = event.get("competitions", [])

        if not competitions:
            continue

        competition = competitions[0]
        competitors = competition.get("competitors", [])

        home_team = None
        away_team = None

        for competitor in competitors:
            team = competitor.get("team", {})
            abbreviation = team.get("abbreviation")
            home_away = competitor.get("homeAway")

            if home_away == "home":
                home_team = abbreviation

            elif home_away == "away":
                away_team = abbreviation

        if not home_team or not away_team:
            continue

        kickoff_raw = event.get("date")

        if not kickoff_raw:
            continue

        kickoff = datetime.fromisoformat(
            kickoff_raw.replace("Z", "+00:00")
        )

        games.append(
            RawGameData(
                week=week,
                kickoff=kickoff,
                away_team=away_team,
                home_team=home_team,
            )
        )

    return games
