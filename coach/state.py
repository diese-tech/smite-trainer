from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GameState:
    health_pct: float = -1.0   # 0–100, -1 = unreadable
    mana_pct: float   = -1.0   # 0–100, -1 = unreadable
    gold: int         = -1     # current gold, -1 = unreadable
    timestamp: float  = 0.0    # time.monotonic() of last update
