"""Smite Trainer — entry point.

Starts the overlay window and the game-state capture loop.
The capture loop runs in a background thread and feeds coaching
messages into the overlay via update_message().

Usage:
    python main.py           # normal run
    python main.py --debug   # saves region snapshots to debug/ every tick
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time

import cv2
from PyQt6.QtWidgets import QApplication

from capture.screen import GameWindow
from capture.regions import REGIONS
from coach.rules import CoachingRules
from coach.state import GameState
from overlay import OverlayWindow
from vision.gold import read_gold
from vision.health import read_health, read_mana

_CAPTURE_INTERVAL = 0.5   # seconds between screen reads (2 fps)
_FIND_RETRY       = 3.0   # seconds between window-find retries


def _capture_loop(overlay: OverlayWindow, debug: bool) -> None:
    window = GameWindow()
    rules  = CoachingRules()

    if debug:
        os.makedirs("debug", exist_ok=True)

    tick = 0
    while True:
        # --- Locate game window ---
        if not window.is_ready():
            if not window.find():
                time.sleep(_FIND_RETRY)
                continue

        # --- Grab each HUD region ---
        frames = {name: window.capture_region(r) for name, r in REGIONS.items()}

        # If the window disappeared mid-capture, frames will be None
        if any(f is None for f in frames.values()):
            window.find()   # try to relocate
            time.sleep(_CAPTURE_INTERVAL)
            continue

        # --- Vision ---
        state = GameState(
            health_pct = read_health(frames["health_bar"]),
            mana_pct   = read_mana(frames["mana_bar"], debug=debug),
            gold       = read_gold(frames["gold"]),
            timestamp  = time.monotonic(),
        )

        # --- Debug snapshots ---
        if debug:
            for name, frame in frames.items():
                cv2.imwrite(f"debug/{tick:04d}_{name}.png",
                            cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR))
            print(f"[{tick:04d}] hp={state.health_pct:.1f}%  "
                  f"mp={state.mana_pct:.1f}%  gold={state.gold}")

        # --- Coaching ---
        for message, priority in rules.evaluate(state):
            overlay.update_message(message, priority)

        tick += 1
        time.sleep(_CAPTURE_INTERVAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true",
                        help="Save region snapshots to debug/ and print state")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = OverlayWindow()
    overlay.show()

    thread = threading.Thread(
        target=_capture_loop,
        args=(overlay, args.debug),
        daemon=True,
    )
    thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
