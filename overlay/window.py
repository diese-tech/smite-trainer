from __future__ import annotations

import ctypes

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

from .animator import FadeAnimator
from .message_queue import Message, MessageQueue, Priority

_GWL_EXSTYLE = -20
_WS_EX_LAYERED = 0x00080000
_WS_EX_TRANSPARENT = 0x00000020

_HOLD_MS = 3000

_STYLE: dict[Priority, dict] = {
    Priority.DANGER: {
        "color": "#FF4444",
        "background": "rgba(60, 0, 0, 210)",
        "font_size": 18,
    },
    Priority.OPPORTUNITY: {
        "color": "#FFD700",
        "background": "rgba(35, 28, 0, 200)",
        "font_size": 13,
    },
    Priority.OPTIMIZATION: {
        "color": "#44FF88",
        "background": "rgba(0, 35, 18, 200)",
        "font_size": 13,
    },
}

_BUBBLE_STYLE = (
    "QLabel {{"
    "  color: {color};"
    "  background-color: {background};"
    "  border-radius: 8px;"
    "  padding: 8px 16px;"
    "}}"
)


def _label(parent: QWidget, font_size: int) -> QLabel:
    lbl = QLabel(parent)
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
    lbl.hide()
    return lbl


class OverlayWindow(QWidget):
    """
    Fullscreen transparent click-through overlay.

    Call update_message() from any thread — it is fully thread-safe.
    """

    _incoming = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self._queue = MessageQueue()
        self._build_labels(screen.width(), screen.height())
        self._set_click_through()

        self._incoming.connect(self._handle)

    def update_message(self, text: str, priority: str) -> None:
        """Thread-safe entry point. priority: 'danger' | 'opportunity' | 'optimization'"""
        self._incoming.emit(text, priority)

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_labels(self, w: int, h: int) -> None:
        # --- Danger: centered, 30 % down ---
        danger_w = int(w * 0.36)
        danger_h = 90
        self._danger = _label(self, _STYLE[Priority.DANGER]["font_size"])
        self._danger.setGeometry(
            (w - danger_w) // 2,
            int(h * 0.30),
            danger_w,
            danger_h,
        )
        self._danger_anim = FadeAnimator(self._danger, self)

        # --- Side stack: top-right ---
        side_w = int(w * 0.22)
        side_x = w - side_w - 24
        bubble_h = 62
        gap = 10
        opp_y = int(h * 0.06)

        self._opp = _label(self, _STYLE[Priority.OPPORTUNITY]["font_size"])
        self._opp.setGeometry(side_x, opp_y, side_w, bubble_h)
        self._opp_anim = FadeAnimator(self._opp, self)

        self._opt = _label(self, _STYLE[Priority.OPTIMIZATION]["font_size"])
        self._opt.setGeometry(side_x, opp_y + bubble_h + gap, side_w, bubble_h)
        self._opt_anim = FadeAnimator(self._opt, self)

    # ------------------------------------------------------------------
    # Message handling (runs on main thread via signal)
    # ------------------------------------------------------------------

    def _handle(self, text: str, priority_name: str) -> None:
        msg = self._queue.accept(text, priority_name)
        if msg is None:
            return
        self._display(msg)

    def _display(self, msg: Message) -> None:
        style = _STYLE[msg.priority]
        sheet = _BUBBLE_STYLE.format(**style)

        if msg.priority == Priority.DANGER:
            self._danger.setText(msg.text)
            self._danger.setStyleSheet(sheet)
            self._danger_anim.play(_HOLD_MS, immediate=True)

        elif msg.priority == Priority.OPPORTUNITY:
            self._opp.setText(msg.text)
            self._opp.setStyleSheet(sheet)
            self._opp_anim.play(_HOLD_MS)

        else:  # OPTIMIZATION
            self._opt.setText(msg.text)
            self._opt.setStyleSheet(sheet)
            self._opt_anim.play(_HOLD_MS)

    # ------------------------------------------------------------------
    # Windows click-through
    # ------------------------------------------------------------------

    def _set_click_through(self) -> None:
        try:
            hwnd = int(self.winId())
            cur = ctypes.windll.user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, _GWL_EXSTYLE, cur | _WS_EX_LAYERED | _WS_EX_TRANSPARENT
            )
        except AttributeError:
            pass  # non-Windows; click-through not available
