"""User-supplied SportsLine intelligence layer.

SportsLine subscriber content is intentionally NOT scraped and credentials are never
stored. The dashboard accepts exports/notes supplied by the subscriber and turns
those signals into structured, auditable context for Survivor, Pick'em, and Fantasy.
"""
from __future__ import annotations

import csv
import io
from dataclasses import asdict, dataclass
from typing import Iterable, List


@dataclass
class SportsLineSignal:
    area: str
    subject: str
    recommendation: str
    confidence: float = 0.5
    source: str = "SportsLine"
    notes: str = ""


def _confidence(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.5
    if number > 1:
        number /= 100.0
    return max(0.0, min(1.0, number))


def parse_sportsline_csv(text: str) -> List[SportsLineSignal]:
    """Parse a small, stable import schema without depending on SportsLine HTML."""
    if not text.strip():
        return []
    rows = csv.DictReader(io.StringIO(text))
    signals: List[SportsLineSignal] = []
    for row in rows:
        normalized = {str(k).strip().lower(): (v or "").strip() for k, v in row.items() if k is not None}
        subject = normalized.get("subject") or normalized.get("player") or normalized.get("matchup") or normalized.get("team")
        recommendation = normalized.get("recommendation") or normalized.get("pick") or normalized.get("signal")
        if not subject or not recommendation:
            continue
        signals.append(
            SportsLineSignal(
                area=(normalized.get("area") or normalized.get("type") or "General").title(),
                subject=subject,
                recommendation=recommendation,
                confidence=_confidence(normalized.get("confidence", 0.5)),
                source=normalized.get("source") or "SportsLine",
                notes=normalized.get("notes") or normalized.get("analysis") or "",
            )
        )
    return signals


def serialize_signals(signals: Iterable[SportsLineSignal]) -> list[dict]:
    return [asdict(signal) for signal in signals]


def summarize_signals(signals: Iterable[SportsLineSignal], area: str | None = None) -> dict:
    selected = [s for s in signals if area is None or s.area.lower() == area.lower()]
    if not selected:
        return {"count": 0, "average_confidence": 0.0, "high_confidence": []}
    high = sorted(selected, key=lambda s: s.confidence, reverse=True)[:5]
    return {
        "count": len(selected),
        "average_confidence": sum(s.confidence for s in selected) / len(selected),
        "high_confidence": serialize_signals(high),
    }


CSV_TEMPLATE = """area,subject,recommendation,confidence,source,notes
Survivor,LAC,Strong survivor play,0.82,SportsLine Model,Optional note
Pickem,KC vs DEN,KC,0.58,SportsLine Model,Optional note
Fantasy,Player Name,Start,0.75,SportsLine Expert,Optional note
"""
