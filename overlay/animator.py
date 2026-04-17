from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

_FADE_IN_MS = 300
_FADE_OUT_MS = 500


class FadeAnimator(QObject):
    """Drives a fade-in → hold → fade-out lifecycle for a single widget."""

    finished = pyqtSignal()

    def __init__(self, widget: QWidget, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget = widget

        self._effect = QGraphicsOpacityEffect(widget)
        self._effect.setOpacity(0.0)
        widget.setGraphicsEffect(self._effect)

        self._fade_in = QPropertyAnimation(self._effect, b"opacity", self)
        self._fade_in.setDuration(_FADE_IN_MS)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._fade_out = QPropertyAnimation(self._effect, b"opacity", self)
        self._fade_out.setDuration(_FADE_OUT_MS)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_out.finished.connect(self._on_done)

        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._fade_out.start)

    def play(self, hold_ms: int, immediate: bool = False) -> None:
        """Show the widget. If immediate=True, skip fade-in (danger interrupt)."""
        self._cancel()
        self._widget.show()
        if immediate:
            self._effect.setOpacity(1.0)
            self._hold_timer.start(hold_ms)
        else:
            self._fade_in.start()
            self._hold_timer.start(hold_ms + _FADE_IN_MS)

    def stop(self) -> None:
        """Hide immediately without finishing the animation."""
        self._cancel()
        self._effect.setOpacity(0.0)
        self._widget.hide()

    # ------------------------------------------------------------------

    def _cancel(self) -> None:
        self._hold_timer.stop()
        self._fade_in.stop()
        self._fade_out.stop()

    def _on_done(self) -> None:
        self._widget.hide()
        self.finished.emit()
