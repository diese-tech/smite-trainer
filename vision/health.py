from __future__ import annotations

import cv2
import numpy as np

# HSV ranges for the Smite 2 health bar fill colour (green → yellow → red).
# We count any "coloured" pixel in the bar as "filled" vs the dark background.
_HEALTH_LOW  = np.array([35,  60,  60],  dtype=np.uint8)   # yellow-green floor
_HEALTH_HIGH = np.array([85, 255, 255],  dtype=np.uint8)   # green ceiling

# HSV range for the mana bar (blue).
_MANA_LOW  = np.array([100,  80,  80],  dtype=np.uint8)
_MANA_HIGH = np.array([140, 255, 255],  dtype=np.uint8)


def _bar_fill_pct(frame: np.ndarray, low: np.ndarray, high: np.ndarray) -> float:
    """
    Return the fill percentage (0–100) of a coloured bar in frame.

    Works by counting pixels that match the target colour range along
    the horizontal axis; the rightmost matching column marks the fill end.
    """
    if frame is None or frame.size == 0:
        return -1.0

    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)

    cols = np.any(mask > 0, axis=0)  # True for each column that has a match
    if not np.any(cols):
        return 0.0

    filled = int(np.argwhere(cols)[-1][0]) + 1  # rightmost filled column (1-indexed)
    return round(filled / mask.shape[1] * 100, 1)


def read_health(frame: np.ndarray) -> float:
    """Return player health as a percentage (0–100). -1 if unreadable."""
    return _bar_fill_pct(frame, _HEALTH_LOW, _HEALTH_HIGH)


def read_mana(frame: np.ndarray) -> float:
    """Return player mana as a percentage (0–100). -1 if unreadable."""
    return _bar_fill_pct(frame, _MANA_LOW, _MANA_HIGH)
