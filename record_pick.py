import argparse

from state import load_state, save_state


def main():
    parser = argparse.ArgumentParser(
        description="Record an official NFL pool pick."
    )

    parser.add_argument(
        "--week",
        type=int,
        required=True,
        help="NFL week number",
    )

    parser.add_argument(
        "--team",
        type=str,
        required=True,
        help="NFL team abbreviation",
    )

    args = parser.parse_args()

    team = args.team.upper().strip()
    week = args.week

    state = load_state()

    if team in state.survivor_used_teams:
        raise ValueError(
            f"{team} has already been used in Survivor."
        )

    existing_pick = state.survivor_picks.get(week)

    if existing_pick:
        raise ValueError(
            f"Week {week} already has Survivor pick "
            f"{existing_pick}."
        )

    state.record_survivor_pick(
        week=week,
        team=team,
    )

    state.current_week = max(
        state.current_week,
        week,
    )

    save_state(state)

    print("=== SURVIVOR PICK RECORDED ===")
    print(f"Week: {week}")
    print(f"Team: {team}")
    print(
        "Used teams: "
        f"{sorted(state.survivor_used_teams)}"
    )


if __name__ == "__main__":
    main()
