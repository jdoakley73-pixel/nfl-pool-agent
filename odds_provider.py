import requests

from odds import remove_vig


ESPN_ODDS_URL = (
    "https://sports.core.api.espn.com/v2/"
    "sports/football/leagues/nfl/events/{event_id}/"
    "competitions/{event_id}/odds"
)


def fetch_event_odds(event_id: str) -> dict | None:
    """
    Fetch available sportsbook odds for one NFL event.

    Returns the highest-priority provider ESPN supplies.
    """

    url = ESPN_ODDS_URL.format(event_id=event_id)

    response = requests.get(
        url,
        params={"limit": 10},
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    items = payload.get("items", [])

    if not items:
        return None

    # ESPN generally orders providers by priority.
    odds = items[0]

    home_odds = odds.get("homeTeamOdds") or {}
    away_odds = odds.get("awayTeamOdds") or {}

    home_moneyline = home_odds.get("moneyLine")
    away_moneyline = away_odds.get("moneyLine")

    if (
        home_moneyline is None
        or away_moneyline is None
    ):
        return None

    home_probability, away_probability = remove_vig(
        home_moneyline=home_moneyline,
        away_moneyline=away_moneyline,
    )

    provider = odds.get("provider") or {}

    return {
        "provider": provider.get("name", "Unknown"),
        "home_moneyline": home_moneyline,
        "away_moneyline": away_moneyline,
        "home_win_probability": home_probability,
        "away_win_probability": away_probability,
        "spread": odds.get("spread"),
        "total": odds.get("overUnder"),
    }
