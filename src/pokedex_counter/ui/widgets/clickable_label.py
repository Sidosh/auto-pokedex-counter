from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
)

class ClickableLabel(QLabel):
    clicked = Signal(Path)

    BASE_STYLE = "padding: 3px;"

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = path
        self._selected = False
        self.setStyleSheet(self.BASE_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_selected()
        super().mousePressEvent(event)

    def toggle_selected(self) -> None:
        self._selected = not self._selected
        self._apply_style()
        self.clicked.emit(self._path)

    def select(self) -> None:
        """Programmatically select (idempotent - no-op if already selected)."""
        if self._selected:
            return
        self._selected = True
        self._apply_style()
        self.clicked.emit(self._path)

    def _apply_style(self) -> None:
        if self._selected:
            self.setStyleSheet(self.BASE_STYLE + "background-color: black;")
        else:
            self.setStyleSheet(self.BASE_STYLE)