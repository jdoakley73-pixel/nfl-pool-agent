import pandas as pd
import streamlit as st

DEFAULT_ROSTER = [
    {"Player": "Patrick Mahomes", "Pos": "QB", "Team": "KC", "Slot": "QB", "Status": "Starter"},
    {"Player": "Kenneth Walker III", "Pos": "RB", "Team": "KC", "Slot": "RB", "Status": "Starter"},
    {"Player": "Jadarian Price", "Pos": "RB", "Team": "SEA", "Slot": "RB", "Status": "Starter"},
    {"Player": "Justin Jefferson", "Pos": "WR", "Team": "MIN", "Slot": "WR", "Status": "Starter"},
    {"Player": "Ladd McConkey", "Pos": "WR", "Team": "LAC", "Slot": "WR", "Status": "Starter"},
    {"Player": "Mark Andrews", "Pos": "TE", "Team": "BAL", "Slot": "TE", "Status": "Starter"},
    {"Player": "Rome Odunze", "Pos": "WR", "Team": "CHI", "Slot": "W/R/T", "Status": "Starter"},
    {"Player": "Raiders D/ST", "Pos": "DST", "Team": "LV", "Slot": "DEF", "Status": "Starter"},
    {"Player": "Jake Bates", "Pos": "K", "Team": "DET", "Slot": "K", "Status": "Starter"},
    {"Player": "MarShawn Lloyd", "Pos": "RB", "Team": "GB", "Slot": "BN", "Status": "Bench"},
    {"Player": "Chris Godwin Jr.", "Pos": "WR", "Team": "TB", "Slot": "BN", "Status": "Bench"},
    {"Player": "KC Concepcion", "Pos": "WR", "Team": "CLE", "Slot": "BN", "Status": "Bench"},
    {"Player": "Romeo Doubs", "Pos": "WR", "Team": "NE", "Slot": "BN", "Status": "Bench"},
    {"Player": "Dalton Schultz", "Pos": "TE", "Team": "HOU", "Slot": "BN", "Status": "Bench"},
    {"Player": "Brian Robinson Jr.", "Pos": "RB", "Team": "ATL", "Slot": "BN", "Status": "Bench"},
    {"Player": "Keenan Allen", "Pos": "WR", "Team": "IND", "Slot": "BN", "Status": "Bench"},
    {"Player": "Jordyn Tyson", "Pos": "WR", "Team": "NO", "Slot": "IR", "Status": "IR"},
]


def render_weekly_gm():
    if "weekly_roster" not in st.session_state:
        st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)

    st.markdown("### Weekly Fantasy GM")
    st.caption("Harold Whigskin • 12 teams • Half PPR • 6-pt pass TD • 1 pt / 20 pass yds • -1 per QB sack")

    roster = st.session_state.weekly_roster.copy()
    active = roster[roster["Status"].isin(["Starter", "Bench"])]
    starters = roster[roster["Status"] == "Starter"]
    bench = roster[roster["Status"] == "Bench"]
    ir = roster[roster["Status"] == "IR"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active roster", len(active))
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
        st.success("✅ Starting lineup is complete — QB/RB/RB/WR/WR/TE/FLEX/K/DEF filled.")

    lineup_order = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "W/R/T": 5, "K": 6, "DEF": 7, "BN": 8, "IR": 9}
    display = roster.copy()
    display["_order"] = display["Slot"].map(lineup_order).fillna(99)
    display = display.sort_values(["_order", "Slot", "Player"]).drop(columns=["_order"])

    st.markdown("#### Current lineup")
    st.dataframe(display, use_container_width=True, hide_index=True, height=560)

    st.markdown("#### Roster manager")
    st.caption("Edit players, positions, teams or slots below, then hit Save roster.")
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
        key="weekly_roster_editor_inline",
    )

    c1, c2 = st.columns(2)
    if c1.button("💾 Save roster", use_container_width=True, type="primary", key="save_weekly_roster_inline"):
        st.session_state.weekly_roster = edited.copy()
        st.rerun()
    if c2.button("↩️ Reset post-draft setup", use_container_width=True, key="reset_weekly_roster_inline"):
        st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)
        st.rerun()

    with st.expander("Loaded post-draft moves"):
        st.write("• Jordyn Tyson → IR")
        st.write("• Malik Willis → dropped")
        st.write("• Raiders D/ST → Week 1 defense")
        st.write("• Jake Bates → Week 1 kicker")
        st.write("• Dalton Schultz → bench behind Mark Andrews")

    st.markdown("#### Weekly GM checklist")
    st.write("Tuesday waivers → Thursday lineup/injury check → Saturday roster audit → Sunday final lock")
    st.info("Yahoo remains the official transaction/lineup venue until read-only API sync is connected.")