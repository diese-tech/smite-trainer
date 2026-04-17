"""Entry point and manual demo.

Run this to see the overlay in action with sample messages.
"""
from __future__ import annotations

import sys
import threading
import time

from PyQt6.QtWidgets import QApplication

from overlay import OverlayWindow


def _demo(overlay: OverlayWindow) -> None:
    time.sleep(1.0)
    overlay.update_message("🟢 Level 2 first — pressure now", "opportunity")

    time.sleep(1.5)
    overlay.update_message("💡 Ward river — vision gap", "optimization")

    time.sleep(2.5)
    # Danger cuts in immediately over whatever is showing
    overlay.update_message("⚠️ Jungle missing — back up!", "danger")

    time.sleep(4.0)
    overlay.update_message("🟢 Enemy low — dive now", "opportunity")

    time.sleep(2.0)
    # Duplicate opportunity within cooldown — should be silently dropped
    overlay.update_message("🟢 This should be suppressed", "opportunity")

    time.sleep(2.5)
    overlay.update_message("💡 Buy mana pot before next rotation", "optimization")


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = OverlayWindow()
    overlay.show()

    threading.Thread(target=_demo, args=(overlay,), daemon=True).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
