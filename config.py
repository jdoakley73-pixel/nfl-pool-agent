from dataclasses import dataclass


@dataclass(frozen=True)
class PoolConfig:
    season: int = 2026

    # Pick'em rules
    pickem_all_games: bool = True
    pickem_uses_spread: bool = False
    pickem_confidence_points: bool = False
    pickem_mnf_tiebreaker: bool = True
    pickem_playoffs: bool = False

    # Survivor rules
    survivor_picks_per_week: int = 1
    survivor_team_reuse: bool = False
    survivor_tie_is_loss: bool = True
    survivor_playoffs: bool = False


CONFIG = PoolConfig()
