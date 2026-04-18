from __future__ import annotations

import re

import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Tesseract config: single line, digits only, LSTM engine.
_OCR_CONFIG = "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"

_DIGIT_RE = re.compile(r"\d+")


def read_gold(frame: np.ndarray) -> int:
    """
    Return the player's current gold as an integer.
    Returns -1 if the region is unreadable or Tesseract is not installed.
    """
    if frame is None or frame.size == 0:
        return -1

    # Skip left 25% — that's the coin icon, not the number.
    h, w = frame.shape[:2]
    frame = frame[:, int(w * 0.25):]

    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # Gold number is near-white (low saturation, high brightness).
    # Item icons are colourful (high saturation) — this filter excludes them.
    mask = cv2.inRange(hsv, np.array([0, 0, 160], dtype=np.uint8),
                            np.array([179, 50, 255], dtype=np.uint8))
    mask = cv2.bitwise_not(mask)

    # Upscale — Tesseract reads larger text more accurately.
    mask = cv2.resize(mask, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)

    # Always save the last processed mask so it can be inspected.
    try:
        import os
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/gold_mask.png", mask)
    except Exception:
        pass

    try:
        raw = pytesseract.image_to_string(mask, config=_OCR_CONFIG).strip()
    except Exception:
        return -1

    digits = _DIGIT_RE.findall(raw)
    if not digits:
        return -1

    try:
        value = int(digits[0])
        return value if value <= 9999 else -1  # sanity cap
    except ValueError:
        return -1
