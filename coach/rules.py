from __future__ import annotations

import time
from dataclasses import dataclass, field

from .state import GameState

# Thresholds
_HEALTH_DANGER     = 25.0   # % — immediate danger
_HEALTH_WARNING    = 40.0   # % — caution
_MANA_LOW          = 20.0   # %
_GOLD_THRESHOLD    = 1500   # g — enough for a meaningful item
_GOLD_WARN_DELAY   = 10.0   # seconds gold must sit above threshold before warning


@dataclass
class _RuleState:
    """Internal timer/flag state tracked across evaluate() calls."""
    gold_high_since: float | None = None


class CoachingRules:
    def __init__(self) -> None:
        self._rs = _RuleState()

    def evaluate(self, state: GameState) -> list[tuple[str, str]]:
        """
        Compare current game state against coaching rules.
        Returns a list of (message, priority) pairs to send to the overlay.
        Priority: 'danger' | 'opportunity' | 'optimization'
        """
        msgs: list[tuple[str, str]] = []
        now = time.monotonic()

        # --- Health ---
        if 0 <= state.health_pct < _HEALTH_DANGER:
            msgs.append(("⚠️ Critical HP — back up NOW", "danger"))
        elif 0 <= state.health_pct < _HEALTH_WARNING:
            msgs.append(("⚠️ Low HP — play safe", "danger"))

        # --- Mana ---
        if 0 <= state.mana_pct < _MANA_LOW:
            msgs.append(("💧 Low mana — rotate back", "optimization"))

        # --- Gold sitting too long ---
        if state.gold >= _GOLD_THRESHOLD:
            if self._rs.gold_high_since is None:
                self._rs.gold_high_since = now
            elif now - self._rs.gold_high_since >= _GOLD_WARN_DELAY:
                msgs.append(("💰 Too much gold — hit the shop", "opportunity"))
        else:
            # Gold dropped — player spent it, reset the timer
            self._rs.gold_high_since = None

        return msgs
