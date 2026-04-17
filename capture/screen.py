from __future__ import annotations

import numpy as np
import mss
import win32gui

# Case-insensitive substring matched against window titles.
_GAME_TITLE = "smite 2"


class GameWindow:
    """Locates the Smite 2 window and captures pixel regions from it."""

    def __init__(self) -> None:
        self._sct = mss.mss()
        self.hwnd: int | None = None
        self._bounds: dict | None = None  # left, top, width, height of client area

    # ------------------------------------------------------------------
    # Window detection
    # ------------------------------------------------------------------

    def find(self) -> bool:
        """Scan all visible windows for Smite 2. Returns True if found."""
        found: list[int] = []

        def _visit(hwnd: int, _) -> None:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if _GAME_TITLE in title:
                    found.append(hwnd)

        win32gui.EnumWindows(_visit, None)

        if not found:
            self.hwnd = None
            self._bounds = None
            return False

        self.hwnd = found[0]
        self._refresh_bounds()
        return True

    def is_ready(self) -> bool:
        return self._bounds is not None

    # ------------------------------------------------------------------
    # Capture
    # ------------------------------------------------------------------

    def capture_region(self, region: dict) -> np.ndarray | None:
        """
        Capture a sub-region of the game client area.

        region keys: x, y, w, h — all as fractions of client width/height.
        Returns an BGRA numpy array, or None if the window is gone.
        """
        if not self._bounds:
            return None

        b = self._bounds
        left = b["left"] + int(region["x"] * b["width"])
        top  = b["top"]  + int(region["y"] * b["height"])
        w    = max(1, int(region["w"] * b["width"]))
        h    = max(1, int(region["h"] * b["height"]))

        try:
            shot = self._sct.grab({"left": left, "top": top, "width": w, "height": h})
            return np.array(shot)  # BGRA
        except mss.exception.ScreenShotError:
            self._bounds = None
            return None

    def capture_full(self) -> np.ndarray | None:
        """Capture the entire game client area."""
        if not self._bounds:
            return None
        try:
            shot = self._sct.grab(self._bounds)
            return np.array(shot)
        except mss.exception.ScreenShotError:
            self._bounds = None
            return None

    # ------------------------------------------------------------------

    def _refresh_bounds(self) -> None:
        if not self.hwnd:
            return
        try:
            left, top = win32gui.ClientToScreen(self.hwnd, (0, 0))
            cr = win32gui.GetClientRect(self.hwnd)
            self._bounds = {
                "left": left,
                "top": top,
                "width": cr[2],
                "height": cr[3],
            }
        except Exception:
            self._bounds = None

    def __del__(self) -> None:
        try:
            self._sct.close()
        except Exception:
            pass
