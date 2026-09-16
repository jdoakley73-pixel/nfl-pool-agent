def set_survivor_pick_compat(pool_state, week: int, team: str) -> None:
    """Record/correct a Survivor pick while keeping used teams synchronized."""
    team = team.strip().upper()
    previous = pool_state.survivor_picks.get(week)
    if previous == team:
        return
    if team in pool_state.survivor_used_teams and team != previous:
        raise ValueError(f"{team} has already been used in Survivor.")
    if previous:
        pool_state.survivor_used_teams.discard(previous)
    pool_state.survivor_picks[week] = team
    pool_state.survivor_used_teams.add(team)


def advance_week_compat(pool_state, week: int) -> None:
    week = int(week)
    if not 1 <= week <= 18:
        raise ValueError("NFL week must be between 1 and 18.")
    pool_state.current_week = week
