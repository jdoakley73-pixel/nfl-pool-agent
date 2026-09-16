from state import PoolState
from survivor_runtime_compat import set_survivor_pick_compat, advance_week_compat

state = PoolState()
set_survivor_pick_compat(state, 1, "JAX")
assert state.survivor_picks[1] == "JAX"
assert "JAX" in state.survivor_used_teams

set_survivor_pick_compat(state, 1, "LAC")
assert state.survivor_picks[1] == "LAC"
assert "LAC" in state.survivor_used_teams
assert "JAX" not in state.survivor_used_teams

advance_week_compat(state, 2)
assert state.current_week == 2

print("Survivor dashboard compatibility helpers passed")
