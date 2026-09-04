import pandas as pd
import streamlit as st

# Final Yahoo roster confirmed from the post-draft roster screenshots.
ROSTER_VERSION = "2026-week1-final-v2"
DEFAULT_ROSTER = [
    {"Player": "Patrick Mahomes", "Pos": "QB", "Team": "KC", "Slot": "QB", "Status": "Starter"},
    {"Player": "Kenneth Walker III", "Pos": "RB", "Team": "KC", "Slot": "RB", "Status": "Starter"},
    {"Player": "MarShawn Lloyd", "Pos": "RB", "Team": "GB", "Slot": "RB", "Status": "Starter"},
    {"Player": "Justin Jefferson", "Pos": "WR", "Team": "MIN", "Slot": "WR", "Status": "Starter"},
    {"Player": "Ladd McConkey", "Pos": "WR", "Team": "LAC", "Slot": "WR", "Status": "Starter"},
    {"Player": "Mark Andrews", "Pos": "TE", "Team": "BAL", "Slot": "TE", "Status": "Starter"},
    {"Player": "Rome Odunze", "Pos": "WR", "Team": "CHI", "Slot": "W/R/T", "Status": "Starter"},
    {"Player": "Jake Bates", "Pos": "K", "Team": "DET", "Slot": "K", "Status": "Starter"},
    {"Player": "Raiders D/ST", "Pos": "DST", "Team": "LV", "Slot": "DEF", "Status": "Starter"},
    {"Player": "Jadarian Price", "Pos": "RB", "Team": "SEA", "Slot": "BN", "Status": "Bench"},
    {"Player": "Chris Godwin Jr.", "Pos": "WR", "Team": "TB", "Slot": "BN", "Status": "Bench"},
    {"Player": "KC Concepcion", "Pos": "WR", "Team": "CLE", "Slot": "BN", "Status": "Bench"},
    {"Player": "Romeo Doubs", "Pos": "WR", "Team": "NE", "Slot": "BN", "Status": "Bench"},
    {"Player": "Brian Robinson Jr.", "Pos": "RB", "Team": "ATL", "Slot": "BN", "Status": "Bench"},
    {"Player": "Keenan Allen", "Pos": "WR", "Team": "IND", "Slot": "BN", "Status": "Bench"},
    {"Player": "Jordyn Tyson", "Pos": "WR", "Team": "NO", "Slot": "IR", "Status": "IR"},
]


def _initialize_roster():
    # Versioning forces old Streamlit sessions off the obsolete post-draft roster.
    if st.session_state.get("weekly_roster_version") != ROSTER_VERSION:
        st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)
        st.session_state.weekly_roster_version = ROSTER_VERSION
    elif "weekly_roster" not in st.session_state:
        st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)


def render_weekly_gm():
    _initialize_roster()

    st.markdown("### Weekly Fantasy GM")
    st.caption("Harold Whigskin • 12 teams • Half PPR • 6-pt pass TD • 1 pt / 20 pass yds • -1 per QB sack")

    roster = st.session_state.weekly_roster.copy()
    active = roster[roster["Status"].isin(["Starter", "Bench"])]
    starters = roster[roster["Status"] == "Starter"]
    bench = roster[roster["Status"] == "Bench"]
    ir = roster[roster["Status"] == "IR"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active", len(active))
    m2.metric("Starters", len(starters))
    m3.metric("Bench", len(bench))
    m4.metric("IR", len(ir))

    required = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "W/R/T": 1, "K": 1, "DEF": 1}
    missing = []
    for slot, needed in required.items():
        have = int((starters["Slot"] == slot).sum())
        if have < needed:
            missing.append(f"{slot} x{needed - have}")

    if missing:
        st.error("Starting lineup incomplete: " + ", ".join(missing))
    else:
        st.success("✅ Yahoo lineup mirrored — all 9 starting slots filled.")

    st.markdown("#### GM action board")
    st.warning("⚠️ WATCH: Patrick Mahomes and Rome Odunze are currently tagged Q on the Yahoo roster. Recheck status before their games.")
    st.info("🩼 IR: Jordyn Tyson is correctly stashed in IR. No active roster spot consumed.")
    st.write("**Priority:** injury/Q check → start/sit optimization → waiver upgrades → K/DST stream → final lineup lock")

    lineup_order = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "W/R/T": 5, "K": 6, "DEF": 7, "BN": 8, "IR": 9}
    display = roster.copy()
    display["_order"] = display["Slot"].map(lineup_order).fillna(99)
    display = display.sort_values(["_order", "Slot", "Player"]).drop(columns=["_order"])

    st.markdown("#### Current Yahoo roster")
    st.dataframe(display, use_container_width=True, hide_index=True, height=560)

    st.markdown("#### Roster manager")
    st.caption("Use this after a Yahoo add/drop or lineup move. Save once the app matches Yahoo.")
    edited = st.data_editor(
        roster,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Pos": st.column_config.SelectboxColumn("Pos", options=["QB", "RB", "WR", "TE", "K", "DST"]),
            "Slot": st.column_config.SelectboxColumn("Slot", options=["QB", "RB", "WR", "TE", "W/R/T", "K", "DEF", "BN", "IR"]),
            "Status": st.column_config.SelectboxColumn("Status", options=["Starter", "Bench", "IR"]),
        },
        key="weekly_roster_editor_inline_v2",
    )

    c1, c2 = st.columns(2)
    if c1.button("💾 Save roster", use_container_width=True, type="primary", key="save_weekly_roster_inline_v2"):
        st.session_state.weekly_roster = edited.copy()
        st.rerun()
    if c2.button("↩️ Restore Yahoo snapshot", use_container_width=True, key="reset_weekly_roster_inline_v2"):
        st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)
        st.rerun()

    with st.expander("Starters", expanded=False):
        st.dataframe(starters[["Player", "Pos", "Team", "Slot"]], use_container_width=True, hide_index=True)
    with st.expander("Bench + IR", expanded=False):
        st.dataframe(roster[roster["Status"].isin(["Bench", "IR"])][["Player", "Pos", "Team", "Slot", "Status"]], use_container_width=True, hide_index=True)

    st.markdown("#### Weekly workflow")
    st.write("Tuesday waivers → Thursday injury/start-sit check → Saturday roster audit → Sunday final lock")
    st.caption("Yahoo remains the official transaction and lineup venue until Yahoo read-only API sync is connected.")