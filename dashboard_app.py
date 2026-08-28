import pandas as pd
import streamlit as st

from dashboard_service import build_command_center_data
from state import load_state


st.set_page_config(
    page_title="NFL Pool Command Center",
    page_icon="🏈",
    layout="wide",
)

st.title("🏈 NFL Pool Command Center")
st.caption("Live Survivor + Pick'em recommendations powered by the pool agent.")

state = load_state()

with st.sidebar:
    st.header("Pool settings")
    pool_size = st.number_input(
        "Estimated Survivor entries",
        min_value=2,
        max_value=5000,
        value=75,
        step=1,
    )
    st.metric("Season", state.season)
    st.metric("Current week", state.current_week)
    if state.survivor_used_teams:
        st.write("**Used Survivor teams**")
        st.write(", ".join(sorted(state.survivor_used_teams)))
    else:
        st.write("**Used Survivor teams:** none")

    if st.button("Refresh live data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=1800, show_spinner=False)
def load_dashboard_snapshot(pool_size_value: int):
    return build_command_center_data(
        state=load_state(),
        pool_size=pool_size_value,
    )


with st.spinner("Building the live pool board…"):
    try:
        snapshot = load_dashboard_snapshot(int(pool_size))
    except Exception as exc:
        st.error("The live board could not be generated right now.")
        st.exception(exc)
        st.stop()

survivor_tab, pickem_tab = st.tabs(["🛡️ Survivor", "✅ Pick'em"])

with survivor_tab:
    decision = snapshot["survivor_decision"]
    primary = decision["recommended_score"]
    alternative = decision.get("alternative_score")

    st.subheader(f"Week {snapshot['current_week']} Survivor call")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pick", decision["recommended_team"])
    col2.metric("Win probability", f"{primary['win_probability']:.1%}")
    col3.metric("Est. ownership", f"{primary['estimated_ownership']:.1%}")
    col4.metric("Verdict", decision["verdict"])

    st.success(decision["reason"])

    if alternative:
        st.markdown("### Best alternative")
        alt1, alt2, alt3 = st.columns(3)
        alt1.metric("Team", alternative["team"])
        alt2.metric(
            "Win probability",
            f"{alternative['win_probability']:.1%}",
        )
        alt3.metric(
            "Est. ownership",
            f"{alternative['estimated_ownership']:.1%}",
        )

    st.markdown("### Pool context")
    ctx1, ctx2, ctx3 = st.columns(3)
    ctx1.metric(
        "Expected entries on pick",
        f"{primary['expected_entries']:.1f}",
    )
    ctx2.metric(
        "Best path survival",
        f"{snapshot['best_path_probability']:.3%}",
    )
    ctx3.metric(
        "Entry status",
        "ALIVE" if snapshot["survivor_alive"] else "ELIMINATED",
    )

    st.markdown("### Best remaining path")
    path_rows = [
        {"Week": week, "Team": team}
        for week, team in sorted(snapshot["best_path"].items())
    ]
    st.dataframe(
        pd.DataFrame(path_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Ownership is modeled before lock because PoolHost selections are hidden. "
        "The model keeps current-week survival as the dominant factor."
    )

with pickem_tab:
    st.subheader(f"Week {snapshot['current_week']} Pick'em card")

    pickem_rows = []
    for item in snapshot["pickem_card"]:
        pickem_rows.append(
            {
                "Matchup": item["matchup"],
                "Pick": item["pick"],
                "Win %": round(item["win_probability"] * 100, 1),
                "Confidence": item["confidence"],
                "Leverage": "⚡" if item["leverage_flag"] else "",
            }
        )

    st.dataframe(
        pd.DataFrame(pickem_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Pick'em recommendations currently use market-derived win probability. "
        "Public-pick leverage will be added when reliable selection data is available."
    )

st.divider()
st.caption(
    "PoolHost remains the official submission venue. This dashboard is the decision layer."
)
