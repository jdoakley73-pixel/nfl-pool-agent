import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weekly Fantasy GM", page_icon="🏆", layout="wide")

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

if "weekly_roster" not in st.session_state:
    st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)

st.title("🏆 Weekly Fantasy GM")
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

st.markdown("### Current lineup")
lineup_order = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "W/R/T": 5, "K": 6, "DEF": 7, "BN": 8, "IR": 9}
display = roster.copy()
display["_order"] = display["Slot"].map(lineup_order).fillna(99)
display = display.sort_values(["_order", "Slot", "Player"]).drop(columns=["_order"])
st.dataframe(display, use_container_width=True, hide_index=True, height=560)

st.markdown("### Roster manager")
st.caption("Edit players, positions, teams or slots below. Hit Save roster when you're done.")
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
    key="weekly_roster_editor",
)

c1, c2 = st.columns(2)
if c1.button("💾 Save roster", use_container_width=True, type="primary"):
    st.session_state.weekly_roster = edited.copy()
    st.success("Roster saved for this GM session.")
    st.rerun()

if c2.button("↩️ Reset to post-draft setup", use_container_width=True):
    st.session_state.weekly_roster = pd.DataFrame(DEFAULT_ROSTER)
    st.rerun()

with st.expander("Post-draft moves loaded into this board"):
    st.write("• Jordyn Tyson is parked in IR.")
    st.write("• Malik Willis is removed as the first cut.")
    st.write("• Raiders D/ST is loaded as the Week 1 defense.")
    st.write("• Jake Bates is loaded as the Week 1 kicker.")
    st.write("• Dalton Schultz remains on the bench behind Mark Andrews for now.")

st.markdown("### Weekly GM checklist")
st.write("1. Tuesday: waiver claims / free-agent upgrades")
st.write("2. Thursday: injury + lineup check")
st.write("3. Saturday: roster audit")
st.write("4. Sunday: final inactive/start-sit check")

st.info("Yahoo API access is still read-only, so this page is the season control panel until automatic roster sync is available.")
