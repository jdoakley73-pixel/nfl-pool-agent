import pandas as pd
import streamlit as st

from dashboard_service import build_command_center_data
from fantasy_gm import DraftPlayer, rank_draft_board, roster_counts
from state import load_state

st.set_page_config(page_title="Football Command Center", page_icon="🏈", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {padding: 0.15rem 0 0.35rem 0;}
    div[data-testid="stMetricLabel"] {font-size: 0.85rem;}
    div[data-testid="stMetricValue"] {font-size: 2rem;}
    .stAlert {padding-top: 0.7rem; padding-bottom: 0.7rem;}
    @media (max-width: 768px) {
        .block-container {padding-left: 1rem; padding-right: 1rem; padding-top: 0.8rem;}
        h1 {font-size: 2.25rem !important; line-height: 1.05 !important;}
        h2 {font-size: 1.65rem !important; margin-top: 0.8rem !important;}
        h3 {font-size: 1.25rem !important; margin-top: 0.6rem !important;}
        div[data-testid="stMetricValue"] {font-size: 1.65rem;}
        div[data-testid="stMetric"] {padding-bottom: 0.15rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏈 Football Command Center")
st.caption("Survivor + Pick'em + Fantasy GM")

state = load_state()

with st.sidebar:
    st.header("Command Center")
    pool_size = st.number_input("Estimated Survivor entries", min_value=2, max_value=5000, value=75, step=1)
    st.metric("Season", state.season)
    st.metric("Current week", state.current_week)
    st.write("**Used Survivor teams**")
    st.write(", ".join(sorted(state.survivor_used_teams)) if state.survivor_used_teams else "None")
    if st.button("Refresh live NFL data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

@st.cache_data(ttl=1800, show_spinner=False)
def load_dashboard_snapshot(pool_size_value: int):
    return build_command_center_data(state=load_state(), pool_size=pool_size_value)

with st.spinner("Building the live football board…"):
    try:
        snapshot = load_dashboard_snapshot(int(pool_size))
    except Exception as exc:
        st.error("The live NFL board could not be generated right now.")
        st.exception(exc)
        st.stop()

survivor_tab, pickem_tab, fantasy_tab = st.tabs(["🛡️ Survivor", "✅ Pick'em", "🏆 Fantasy GM"])

with survivor_tab:
    decision = snapshot["survivor_decision"]
    primary = decision["recommended_score"]
    alternative = decision.get("alternative_score")

    st.subheader(f"Week {snapshot['current_week']} Survivor")
    c1, c2 = st.columns(2)
    c1.metric("Pick", decision["recommended_team"])
    c2.metric("Verdict", decision["verdict"])
    c3, c4 = st.columns(2)
    c3.metric("Win probability", f"{primary['win_probability']:.1%}")
    c4.metric("Est. ownership", f"{primary['estimated_ownership']:.1%}")
    st.success(decision["reason"])

    if alternative:
        st.markdown("### Alternative")
        a1, a2, a3 = st.columns(3)
        a1.metric("Team", alternative["team"])
        a2.metric("Win %", f"{alternative['win_probability']:.1%}")
        a3.metric("Ownership", f"{alternative['estimated_ownership']:.1%}")

    st.markdown("### Pool context")
    x1, x2, x3 = st.columns(3)
    x1.metric("Entries on pick", f"{primary['expected_entries']:.1f}")
    x2.metric("Best path", f"{snapshot['best_path_probability']:.3%}")
    x3.metric("Status", "ALIVE" if snapshot["survivor_alive"] else "OUT")

    with st.expander("Best remaining path"):
        st.dataframe(
            pd.DataFrame([
                {"Week": week, "Team": team}
                for week, team in sorted(snapshot["best_path"].items())
            ]),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

    st.caption("Ownership is modeled before lock because PoolHost selections are hidden. Current-week survival stays dominant.")

with pickem_tab:
    st.subheader(f"Week {snapshot['current_week']} Pick'em")
    rows = [
        {
            "Matchup": item["matchup"],
            "Pick": item["pick"],
            "Win %": round(item["win_probability"] * 100, 1),
            "Confidence": item["confidence"],
            "Leverage": "⚡" if item["leverage_flag"] else "",
        }
        for item in snapshot["pickem_card"]
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=520)
    st.caption("Market-derived win probability drives the card; public-pick leverage can be layered in when reliable selection data is available.")

with fantasy_tab:
    st.subheader("Fantasy Football GM")
    draft_mode, weekly_mode = st.tabs(["🎯 Draft", "📋 Weekly GM"])

    with draft_mode:
        st.info("Manual-sync mode until Yahoo access is available. Enter picks as they happen and the board recalculates around your roster.")
        if "draft_roster" not in st.session_state:
            st.session_state.draft_roster = []
        if "draft_pool" not in st.session_state:
            st.session_state.draft_pool = []

        with st.expander("Add player to draft board", expanded=not st.session_state.draft_pool):
            with st.form("add_available_player", clear_on_submit=True):
                p1, p2, p3 = st.columns(3)
                name = p1.text_input("Player")
                position = p2.selectbox("Position", ["RB", "WR", "QB", "TE", "K", "DST"])
                team = p3.text_input("NFL team")
                p4, p5, p6 = st.columns(3)
                rank = p4.number_input("Rank", min_value=1, max_value=500, value=100)
                adp = p5.number_input("ADP", min_value=1.0, max_value=500.0, value=100.0)
                tier = p6.number_input("Tier", min_value=1, max_value=30, value=5)
                add_player = st.form_submit_button("Add to board")
                if add_player and name.strip():
                    st.session_state.draft_pool.append(
                        DraftPlayer(
                            name=name.strip(),
                            position=position,
                            team=team.strip().upper(),
                            rank=int(rank),
                            adp=float(adp),
                            tier=int(tier),
                        )
                    )

        counts = roster_counts(st.session_state.draft_roster)
        board = rank_draft_board(st.session_state.draft_pool, counts)
        if board:
            best = board[0]
            st.success(
                f"Pick now: {best['name']} ({best['position']}) — "
                f"{'fills a starting need' if best['roster_need'] else 'best current value'}."
            )
            st.markdown("### Best available")
            board_df = pd.DataFrame(board)
            board_df["draft_score"] = board_df["draft_score"].round(1)
            st.dataframe(
                board_df[["name", "position", "team", "rank", "adp", "tier", "roster_need", "draft_score"]],
                use_container_width=True,
                hide_index=True,
                height=420,
            )

            drafted_name = st.selectbox("Player just drafted", [row["name"] for row in board])
            d1, d2 = st.columns(2)
            if d1.button("Mine", use_container_width=True):
                player = next(p for p in st.session_state.draft_pool if p.name == drafted_name)
                st.session_state.draft_roster.append(player)
                st.session_state.draft_pool.remove(player)
                st.rerun()
            if d2.button("Someone else", use_container_width=True):
                player = next(p for p in st.session_state.draft_pool if p.name == drafted_name)
                st.session_state.draft_pool.remove(player)
                st.rerun()
        else:
            st.warning("Add available players to start the live draft board.")

        with st.expander("My roster", expanded=True):
            if st.session_state.draft_roster:
                st.dataframe(
                    pd.DataFrame([
                        {"Player": p.name, "Pos": p.position, "Team": p.team}
                        for p in st.session_state.draft_roster
                    ]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.write("No players drafted yet.")

    with weekly_mode:
        st.markdown("### Weekly GM workspace")
        st.info("Bridge mode while Yahoo API access is unresolved. Next up: lineup, bench, waiver, injury/bye alerts and a prioritized GM action list.")
        st.write("Roster snapshot → start/sit → waivers → injury/bye flags → final lineup checklist")

st.divider()
st.caption("PoolHost and Yahoo remain the official submission venues. This is the decision layer.")
