"""Yahoo Fantasy read-only OAuth/API helpers for the Streamlit command center."""
from __future__ import annotations

import base64
import secrets
import time
from typing import Any
from urllib.parse import urlencode

import requests

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
FANTASY_BASE = "https://fantasysports.yahooapis.com/fantasy/v2"


def authorization_url(client_id: str, redirect_uri: str, state: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
        "language": "en-us",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def new_state() -> str:
    return secrets.token_urlsafe(24)


def _basic_auth(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def exchange_code(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict[str, Any]:
    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": _basic_auth(client_id, client_secret),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "authorization_code", "redirect_uri": redirect_uri, "code": code},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    payload["obtained_at"] = int(time.time())
    return payload


def refresh_access_token(client_id: str, client_secret: str, redirect_uri: str, refresh_token: str) -> dict[str, Any]:
    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": _basic_auth(client_id, client_secret),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "refresh_token", "redirect_uri": redirect_uri, "refresh_token": refresh_token},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    payload["obtained_at"] = int(time.time())
    return payload


def token_expired(token: dict[str, Any], skew_seconds: int = 120) -> bool:
    obtained = int(token.get("obtained_at", 0))
    expires = int(token.get("expires_in", 3600))
    return time.time() >= obtained + expires - skew_seconds


def fantasy_get(access_token: str, resource: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = resource if resource.startswith("http") else f"{FANTASY_BASE}/{resource.lstrip('/')}"
    query = {"format": "json"}
    if params:
        query.update(params)
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, params=query, timeout=25)
    response.raise_for_status()
    return response.json()


def discover_nfl_leagues(access_token: str) -> dict[str, Any]:
    # Yahoo's user game collection is the safest first discovery call: no hard-coded league/team keys.
    return fantasy_get(access_token, "users;use_login=1/games;game_codes=nfl/leagues")
