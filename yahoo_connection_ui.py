from __future__ import annotations

import streamlit as st

from yahoo_fantasy import (
    authorization_url,
    discover_nfl_leagues,
    exchange_code,
    new_state,
    refresh_access_token,
    token_expired,
)

DEFAULT_REDIRECT_URI = "https://football-command-center.streamlit.app/"


def _config():
    try:
        yahoo = st.secrets.get("yahoo", {})
        client_id = yahoo.get("client_id", "")
        client_secret = yahoo.get("client_secret", "")
        redirect_uri = yahoo.get("redirect_uri", DEFAULT_REDIRECT_URI)
        return client_id, client_secret, redirect_uri
    except Exception:
        return "", "", DEFAULT_REDIRECT_URI


def _query_value(name: str):
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _ensure_fresh_token(client_id: str, client_secret: str, redirect_uri: str):
    token = st.session_state.get("yahoo_token")
    if not token:
        return None
    if token_expired(token) and token.get("refresh_token"):
        fresh = refresh_access_token(client_id, client_secret, redirect_uri, token["refresh_token"])
        if not fresh.get("refresh_token"):
            fresh["refresh_token"] = token["refresh_token"]
        st.session_state.yahoo_token = fresh
        token = fresh
    return token


def render_yahoo_connection():
    st.markdown("#### Yahoo live connection")
    client_id, client_secret, redirect_uri = _config()

    if not client_id or not client_secret:
        st.info("Yahoo OAuth code is installed. Add the Client ID and Client Secret to Streamlit Secrets to activate it.")
        st.code(
            '[yahoo]\nclient_id = "YOUR_CLIENT_ID"\nclient_secret = "YOUR_CLIENT_SECRET"\nredirect_uri = "https://football-command-center.streamlit.app/"',
            language="toml",
        )
        st.caption("Keep the secret in Streamlit Secrets only — never commit it to GitHub.")
        return

    if "yahoo_oauth_state" not in st.session_state:
        st.session_state.yahoo_oauth_state = new_state()

    error = _query_value("error")
    code = _query_value("code")
    returned_state = _query_value("state")

    if error:
        st.error(f"Yahoo authorization returned: {error}")

    if code and not st.session_state.get("yahoo_token"):
        expected = st.session_state.get("yahoo_oauth_state")
        if not returned_state or returned_state != expected:
            st.error("Yahoo OAuth state check failed. Start the connection again from this dashboard.")
        else:
            try:
                st.session_state.yahoo_token = exchange_code(client_id, client_secret, redirect_uri, code)
                st.query_params.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Yahoo token exchange failed: {exc}")

    try:
        token = _ensure_fresh_token(client_id, client_secret, redirect_uri)
    except Exception as exc:
        token = None
        st.error(f"Yahoo token refresh failed: {exc}")

    if not token:
        auth_url = authorization_url(client_id, redirect_uri, st.session_state.yahoo_oauth_state)
        st.link_button("🔐 Connect Yahoo Fantasy", auth_url, use_container_width=True, type="primary")
        st.caption("Read-only connection. The dashboard cannot add/drop players or change your Yahoo lineup.")
        return

    c1, c2 = st.columns(2)
    c1.success("🟢 Yahoo authenticated")
    if c2.button("Disconnect Yahoo", use_container_width=True):
        st.session_state.pop("yahoo_token", None)
        st.session_state.yahoo_oauth_state = new_state()
        st.rerun()

    if st.button("🏈 Test live Fantasy connection", use_container_width=True):
        try:
            payload = discover_nfl_leagues(token["access_token"])
            st.session_state.yahoo_discovery = payload
            st.success("Yahoo Fantasy answered. Live league discovery is working.")
        except Exception as exc:
            st.error(f"Fantasy API call failed: {exc}")

    if st.session_state.get("yahoo_discovery"):
        with st.expander("Live Yahoo discovery payload", expanded=False):
            st.json(st.session_state.yahoo_discovery)
        st.caption("Next parser step: identify Harold Whigskin and your team key, then replace the manual roster snapshot with live Yahoo data.")
