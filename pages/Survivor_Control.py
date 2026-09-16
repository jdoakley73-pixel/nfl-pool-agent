import streamlit as st

from state import load_state, save_state


NFL_TEAMS = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
    "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
    "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG",
    "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WSH",
]

st.set_page_config(page_title="Survivor Control", page_icon="🛡️", layout="centered")
st.title("🛡️ Survivor Control")
st.caption("Record the team you actually used and control the active pool week.")

state = load_state()

st.subheader("Active week")
week = st.number_input(
    "Current Survivor week",
    min_value=1,
    max_value=18,
    value=int(state.current_week),
    step=1,
)

if st.button("Set active week", use_container_width=True):
    state.advance_to_week(int(week))
    save_state(state)
    st.cache_data.clear()
    st.success(f"Active week set to Week {int(week)}.")
    st.rerun()

st.divider()
st.subheader("Record my Survivor pick")

pick_week = st.number_input(
    "Week selected",
    min_value=1,
    max_value=18,
    value=max(1, min(18, int(state.current_week) - 1 if int(state.current_week) > 1 else 1)),
    step=1,
    key="survivor_pick_week",
)

existing_pick = state.survivor_picks.get(int(pick_week))
available_teams = [
    team for team in NFL_TEAMS
    if team not in state.survivor_used_teams or team == existing_pick
]

if existing_pick and existing_pick in available_teams:
    default_index = available_teams.index(existing_pick)
else:
    default_index = 0

team = st.selectbox(
    "Team I actually selected",
    available_teams,
    index=default_index,
    help="Teams already used in another week are removed from this list.",
)

button_label = "Correct saved pick" if existing_pick else "Save Survivor pick"
if st.button(button_label, type="primary", use_container_width=True):
    try:
        state.set_survivor_pick(int(pick_week), team)
        save_state(state)
        st.cache_data.clear()
        st.success(f"Week {int(pick_week)} saved as {team}. {team} is now burned for future Survivor recommendations.")
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

if existing_pick:
    st.info(f"Saved Week {int(pick_week)} pick: **{existing_pick}**")

st.divider()
st.subheader("Survivor history")
if state.survivor_picks:
    for saved_week, saved_team in sorted(state.survivor_picks.items()):
        marker = "← active" if saved_week == state.current_week else ""
        st.write(f"**Week {saved_week}:** {saved_team} {marker}")
else:
    st.write("No Survivor picks recorded yet.")

st.caption(
    "Recorded teams are excluded from future Survivor paths. State is currently stored by the app; a durable hosted state backend is the next reliability upgrade."
)
