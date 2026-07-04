"""Widget that displays every image in a folder, wrapping onto new rows as the
window is resized."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

from pokedex_counter.ui.widgets.flow_layout import FlowLayout

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}


class ClickableLabel(QLabel):
    """A QLabel that emits `clicked` with its associated path when left-clicked,
    and highlights itself with a black background while selected."""

    clicked = Signal(Path)

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = path
        self._selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._selected = not self._selected
            self.setStyleSheet("background-color: black;" if self._selected else "")
            self.clicked.emit(self._path)
        super().mousePressEvent(event)


class SpriteStrip(QScrollArea):
    """A grid of images, found in `folder`, that wraps onto new rows on resize."""

    sprite_clicked = Signal(Path)

    def __init__(self, folder: Path, sprite_size: int = 24, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._folder = Path(folder)
        self._sprite_size = sprite_size

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._container = QWidget()
        self._layout = FlowLayout(self._container, margin=4, spacing=8)
        self.setWidget(self._container)

        self.reload()

    def reload(self) -> None:
        """Re-scan the folder and refresh the displayed sprites."""
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

    def _discover_images(self) -> list[Path]:
        if not self._folder.is_dir():
            return []
        return sorted(
            p for p in self._folder.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
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
        label.clicked.connect(self.sprite_clicked.emit)
        return label