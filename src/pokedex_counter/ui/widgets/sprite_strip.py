"""Widget that displays every image in a folder, wrapping onto new rows as the
window is resized."""

from pathlib import Path
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QWidget,
)

from pokedex_counter.ui.widgets.flow_layout import FlowLayout

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}


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
            self._selected = not self._selected

            if self._selected:
                self.setStyleSheet(self.BASE_STYLE + "background-color: black;")
            else:
                self.setStyleSheet(self.BASE_STYLE)

            self.clicked.emit(self._path)

        super().mousePressEvent(event)


class SpriteStrip(QWidget):
    sprite_clicked = Signal(Path)
    count_changed = Signal(int)

    def __init__(self, folder: Path, sprite_size: int = 24, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._folder = Path(folder)
        self._sprite_size = sprite_size
        self._count = 0 

        self._layout = FlowLayout(self)

        self.reload()

    def reload(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        paths = self._discover_images()

        if not paths:
            placeholder = QLabel(f"No images found in {self._folder}")
            placeholder.setStyleSheet("color: gray; font-style: italic;")
            self._layout.addWidget(placeholder)
            return

        for path in paths:
            self._layout.addWidget(self._make_sprite_label(path))

    @staticmethod
    def natural_key(path):
        s = path.name
        return [int(t) if t.isdigit() else t.lower()
                for t in re.split(r'(\d+)', s)]

    def _discover_images(self) -> list[Path]:
        if not self._folder.is_dir():
            return []

        return sorted(
            (p for p in self._folder.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS),
            key=lambda p: self.natural_key(p)
        )

    def _make_sprite_label(self, path: Path) -> QLabel:
        label = ClickableLabel(path)
        label.setToolTip(path.name)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            label.setText(f"⚠ {path.name}")
            return label

        scaled = pixmap.scaled(
            self._sprite_size,
            self._sprite_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(scaled)

        # IMPORTANT: connect via handler, not direct emit
        label.clicked.connect(self._on_sprite_clicked)

        return label

    def sizeHint(self):
        return self._layout.sizeHint()

    def minimumSizeHint(self):
        return self._layout.minimumSize()

    def _on_sprite_clicked(self, path: Path) -> None:
        label = self.sender()

        if isinstance(label, ClickableLabel):
            if label._selected:
                self._count += 1
            else:
                self._count -= 1

            self.count_changed.emit(self._count)
            self.sprite_clicked.emit(path)