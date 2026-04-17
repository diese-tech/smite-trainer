from __future__ import annotations

import time
from dataclasses import dataclass
from enum import IntEnum


class Priority(IntEnum):
    OPTIMIZATION = 1
    OPPORTUNITY = 2
    DANGER = 3


# Minimum seconds between accepted messages of the same priority.
# DANGER is always accepted regardless of timing.
_COOLDOWN: dict[Priority, float] = {
    Priority.DANGER: 0.0,
    Priority.OPPORTUNITY: 2.0,
    Priority.OPTIMIZATION: 2.0,
}


@dataclass(frozen=True)
class Message:
    text: str
    priority: Priority


class MessageQueue:
    """Accepts or rejects incoming messages based on priority cooldowns."""

    def __init__(self) -> None:
        self._last_shown: dict[Priority, float] = {}

    def accept(self, text: str, priority_name: str) -> Message | None:
        """Return a Message if it passes the cooldown gate, else None."""
        try:
            priority = Priority[priority_name.upper()]
        except KeyError:
            return None

        now = time.monotonic()
        if now - self._last_shown.get(priority, 0.0) < _COOLDOWN[priority]:
            return None

        self._last_shown[priority] = now
        return Message(text=text, priority=priority)
