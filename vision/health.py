from __future__ import annotations

import cv2
import numpy as np

def _bar_fill_pct(frame: np.ndarray) -> float:
    """
    Return the fill percentage (0–100) of a bar in frame using brightness.

    The filled portion is significantly brighter than the empty dark background.
    Finds the rightmost column whose average brightness exceeds the threshold.
    """
    if frame is None or frame.size == 0:
        return -1.0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    col_brightness = gray.mean(axis=0)  # average brightness per column

    threshold = max(30, col_brightness.max() * 0.25)
    bright_cols = np.where(col_brightness > threshold)[0]

    if bright_cols.size == 0:
        return 0.0

    filled = int(bright_cols[-1]) + 1
    return round(filled / gray.shape[1] * 100, 1)


def read_health(frame: np.ndarray) -> float:
    """Return player health as a percentage (0–100). -1 if unreadable."""
    return _bar_fill_pct(frame)


def read_mana(frame: np.ndarray) -> float:
    """Return player mana as a percentage (0–100). -1 if unreadable."""
    return _bar_fill_pct(frame)
