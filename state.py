import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Set


STATE_FILE = Path("pool_state.json")


@dataclass
class PoolState:
    season: int = 2026
    current_week: int = 1

    # Survivor
    survivor_used_teams: Set[str] = field(default_factory=set)
    survivor_alive: bool = True

    # Pick'em
    pickem_weekly_correct: Dict[int, int] = field(default_factory=dict)
    pickem_weekly_total: Dict[int, int] = field(default_factory=dict)
    pickem_season_points: int = 0

    # Historical selections
    survivor_picks: Dict[int, str] = field(default_factory=dict)
    pickem_picks: Dict[int, Dict[str, str]] = field(default_factory=dict)

    def record_survivor_pick(
        self,
        week: int,
        team: str,
    ) -> None:
        team = team.strip().upper()
        if team in self.survivor_used_teams:
            raise ValueError(
                f"{team} has already been used in Survivor."
            )

        self.survivor_used_teams.add(team)
        self.survivor_picks[week] = team

    def set_survivor_pick(self, week: int, team: str) -> None:
        """Record or correct a Survivor pick while keeping used teams in sync."""
        team = team.strip().upper()
        previous = self.survivor_picks.get(week)

        if previous == team:
            return

        if team in self.survivor_used_teams and team != previous:
            raise ValueError(f"{team} has already been used in Survivor.")

        if previous:
            self.survivor_used_teams.discard(previous)

        self.survivor_picks[week] = team
        self.survivor_used_teams.add(team)

    def advance_to_week(self, week: int) -> None:
        if not 1 <= int(week) <= 18:
            raise ValueError("NFL week must be between 1 and 18.")
        self.current_week = int(week)

    def record_pickem_pick(
        self,
        week: int,
        matchup: str,
        team: str,
    ) -> None:
        if week not in self.pickem_picks:
            self.pickem_picks[week] = {}

        self.pickem_picks[week][matchup] = team

    def record_pickem_result(
        self,
        week: int,
        correct: int,
        total: int,
    ) -> None:
        self.pickem_weekly_correct[week] = correct
        self.pickem_weekly_total[week] = total

        self.pickem_season_points = sum(
            self.pickem_weekly_correct.values()
        )


def save_state(
    state: PoolState,
    path: Path = STATE_FILE,
) -> None:
    data = asdict(state)

    # Sets are not JSON serializable.
    data["survivor_used_teams"] = sorted(
        state.survivor_used_teams
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
        )
    )


def load_state(
    path: Path = STATE_FILE,
) -> PoolState:
    if not path.exists():
        return PoolState()

    data = json.loads(path.read_text())

    data["survivor_used_teams"] = set(
        data.get("survivor_used_teams", [])
    )

    # JSON turns integer dictionary keys into strings.
    for field_name in (
        "pickem_weekly_correct",
        "pickem_weekly_total",
        "survivor_picks",
        "pickem_picks",
    ):
        raw = data.get(field_name, {})
        data[field_name] = {
            int(key): value
            for key, value in raw.items()
        }

    return PoolState(**data)
