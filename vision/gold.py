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

    gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

    # The gold number is bright white text on a dark background.
    # Threshold to isolate bright pixels, then invert for black-on-white OCR.
    _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    mask = cv2.bitwise_not(mask)

    # Clean up noise then upscale — Tesseract reads larger text more accurately.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
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
