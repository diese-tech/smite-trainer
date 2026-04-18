from __future__ import annotations

import cv2
import numpy as np

# Saturation > 60 excludes white/grey text overlay while keeping coloured bar pixels.
# Health bar: green (H 40-90 in OpenCV's 0-179 scale)
_HEALTH_LOW  = np.array([40,  60, 60], dtype=np.uint8)
_HEALTH_HIGH = np.array([90, 255, 255], dtype=np.uint8)

# Mana bar: blue-to-cyan range (Smite 2 uses a teal-blue tone)
_MANA_LOW  = np.array([80,  50, 60], dtype=np.uint8)
_MANA_HIGH = np.array([140, 255, 255], dtype=np.uint8)


def _bar_fill_pct(frame: np.ndarray, low: np.ndarray, high: np.ndarray) -> float:
    """
    Return fill percentage (0–100) by finding the rightmost column that
    contains pixels matching the bar colour. White text is excluded because
    it has near-zero saturation and won't match the colour range.
    """
    if frame is None or frame.size == 0:
        return -1.0

    hsv  = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)

    cols = np.any(mask > 0, axis=0)
    if not np.any(cols):
        return 0.0

    filled = int(np.argwhere(cols)[-1][0]) + 1
    return round(filled / mask.shape[1] * 100, 1)


def read_health(frame: np.ndarray) -> float:
    """Return player health as a percentage (0–100). -1 if unreadable."""
    return _bar_fill_pct(frame, _HEALTH_LOW, _HEALTH_HIGH)


def read_mana(frame: np.ndarray, debug: bool = False) -> float:
    """Return player mana as a percentage (0–100). -1 if unreadable."""
    if debug and frame is not None:
        import os
        os.makedirs("debug", exist_ok=True)
        bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        cv2.imwrite("debug/mana_raw.png", bgr)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        cv2.imwrite("debug/mana_mask.png", cv2.inRange(hsv, _MANA_LOW, _MANA_HIGH))
        # Sample the middle row to find the actual bar colour
        mid = hsv[hsv.shape[0] // 2]
        print(f"[mana HSV mid-row] mean={mid.mean(axis=0).astype(int).tolist()}  "
              f"max={mid.max(axis=0).tolist()}")
    return _bar_fill_pct(frame, _MANA_LOW, _MANA_HIGH)
