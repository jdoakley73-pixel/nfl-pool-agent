from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NFLGame:
    week: int
    kickoff: datetime
    away_team: str
    home_team: str

    away_win_prob: Optional[float] = None
    home_win_prob: Optional[float] = None

    spread: Optional[float] = None
    total: Optional[float] = None

    away_moneyline: Optional[int] = None
    home_moneyline: Optional[int] = None

    venue: Optional[str] = None
    weather_summary: Optional[str] = None

    away_qb_status: Optional[str] = None
    home_qb_status: Optional[str] = None

    is_final: bool = False
    winner: Optional[str] = None

    def favorite(self) -> Optional[str]:
        if self.home_win_prob is None or self.away_win_prob is None:
            return None

        return (
            self.home_team
            if self.home_win_prob >= self.away_win_prob
            else self.away_team
        )

    def favorite_probability(self) -> Optional[float]:
        if self.home_win_prob is None or self.away_win_prob is None:
            return None

        return max(self.home_win_prob, self.away_win_prob)
