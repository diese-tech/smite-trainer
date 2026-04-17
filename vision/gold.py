from __future__ import annotations

import re

import cv2
import numpy as np
import pytesseract

# Smite 2 gold digits are rendered in a bright yellow/gold on a dark background.
_GOLD_LOW  = np.array([18,  120, 120], dtype=np.uint8)   # HSV
_GOLD_HIGH = np.array([38,  255, 255], dtype=np.uint8)

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

    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, _GOLD_LOW, _GOLD_HIGH)

    # Clean up noise then upscale — Tesseract reads larger text more accurately.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.resize(mask, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)

    try:
        raw = pytesseract.image_to_string(mask, config=_OCR_CONFIG).strip()
    except Exception:
        return -1

    digits = _DIGIT_RE.findall(raw)
    if not digits:
        return -1

    try:
        return int(digits[0])
    except ValueError:
        return -1
