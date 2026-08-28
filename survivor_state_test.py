from state import PoolState, save_state, load_state


def main():
    state = PoolState(
        season=2026,
        current_week=1,
    )

    print("=== SURVIVOR STATE TEST ===")
    print()

    print(
        f"Initial used teams: "
        f"{sorted(state.survivor_used_teams)}"
    )

    state.record_survivor_pick(
        week=1,
        team="LAC",
    )

    print(
        f"After Week 1 pick: "
        f"{sorted(state.survivor_used_teams)}"
    )

    save_state(state)

    restored = load_state()

    print(
        f"Restored used teams: "
        f"{sorted(restored.survivor_used_teams)}"
    )

    print(
        f"Week 1 Survivor pick: "
        f"{restored.survivor_picks.get(1)}"
    )

    if "LAC" not in restored.survivor_used_teams:
        raise RuntimeError(
            "Survivor state did not persist correctly."
        )

    print()
    print("Survivor state persistence: PASS")


if __name__ == "__main__":
    main()
