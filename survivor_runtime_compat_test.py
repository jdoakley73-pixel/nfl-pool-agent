from state import PoolState
from survivor_runtime_compat import set_survivor_pick_compat, advance_week_compat

state = PoolState()
set_survivor_pick_compat(state, 1, "JAX")
assert state.survivor_picks[1] == "JAX"
assert state.survivor_used_teams == {"JAX"}

set_survivor_pick_compat(state, 1, "LAC")
assert state.survivor_picks[1] == "LAC"
assert state.survivor_used_teams == {"LAC"}

advance_week_compat(state, 2)
assert state.current_week == 2

try:
    set_survivor_pick_compat(state, 2, "LAC")
    raise AssertionError("Duplicate Survivor team should be rejected")
except ValueError:
    pass

print("Survivor runtime compatibility test passed")
