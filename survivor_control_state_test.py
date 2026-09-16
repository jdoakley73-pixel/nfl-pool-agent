from state import PoolState


def test_pick_tracking_and_correction():
    state = PoolState()
    state.set_survivor_pick(1, "lac")
    assert state.survivor_picks[1] == "LAC"
    assert "LAC" in state.survivor_used_teams

    state.set_survivor_pick(1, "jax")
    assert state.survivor_picks[1] == "JAX"
    assert "JAX" in state.survivor_used_teams
    assert "LAC" not in state.survivor_used_teams


def test_cannot_reuse_team_in_another_week():
    state = PoolState()
    state.set_survivor_pick(1, "LAC")
    try:
        state.set_survivor_pick(2, "LAC")
        raise AssertionError("Expected duplicate Survivor team to be rejected")
    except ValueError:
        pass


def test_week_control():
    state = PoolState()
    state.advance_to_week(2)
    assert state.current_week == 2

    try:
        state.advance_to_week(19)
        raise AssertionError("Expected invalid week to be rejected")
    except ValueError:
        pass


if __name__ == "__main__":
    test_pick_tracking_and_correction()
    test_cannot_reuse_team_in_another_week()
    test_week_control()
    print("Survivor control state tests passed.")
