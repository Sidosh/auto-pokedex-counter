"""Widget that displays every image in a folder, wrapping onto new rows as the
window is resized."""

from pathlib import Path
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QWidget,
)

from pokedex_counter.ui.widgets.clickable_label import ClickableLabel
from pokedex_counter.ui.widgets.flow_layout import FlowLayout

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

class SpriteStrip(QWidget):
    sprite_clicked = Signal(Path)
    sprite_deselected = Signal(str)
    count_changed = Signal(int)

    def __init__(self, folder: Path, sprite_size: int = 24, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._folder = Path(folder)
        self._sprite_size = sprite_size
        self._count = 0
        self._labels_by_name: dict[str, ClickableLabel] = {}
        self._wr_enabled = False
        self._wr_names: set[str] = set()

        self._layout = FlowLayout(self)

        self.reload()

    def reload(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._labels_by_name.clear()
        self._count = 0

        paths = self._discover_images()

        if not paths:
            placeholder = QLabel(f"No images found in {self._folder}")
            placeholder.setStyleSheet("color: gray; font-style: italic;")
            self._layout.addWidget(placeholder)
            return

        for path in paths:
            label = self._make_sprite_label(path)
            self._labels_by_name[path.stem] = label
            self._layout.addWidget(label)

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

    def select_sprite(self, name: str) -> bool:
        label = self._labels_by_name.get(name)
        if label is None:
            return False

        if self._wr_enabled:
            color = "black" if name in self._wr_names else "blue"
        else:
            color = "black"
        label.select(color)
        return True

    def deselect_sprite(self, name: str) -> bool:
        label = self._labels_by_name.get(name)
        if label is None:
            return False

        label.deselect()
        return True

    def mark_wr_section(self, names: set[str]) -> None:
        """Highlight `names` (the current WR section's dex numbers) red, and
        remember them so the next catches are colored black (on-route) or
        blue (off-route) accordingly."""
        self._wr_enabled = True
        self._wr_names = set(names)
        for name, label in self._labels_by_name.items():
            label.set_wr_marked(name in self._wr_names)

    def clear_wr_marks(self) -> None:
        """Turn off WR comparison: no more red highlighting, and catches go
        back to the default black."""
        self._wr_enabled = False
        self._wr_names = set()
        for label in self._labels_by_name.values():
            label.set_wr_marked(False)

    def reset(self) -> None:
        """Deselect every sprite, going through the same per-sprite deselect
        path a manual un-click takes so count/controller/detector state all
        stay consistent."""
        for name in self._labels_by_name:
            self.deselect_sprite(name)

    def set_columns(self, columns: int) -> None:
        self._layout.set_columns(columns)

    def natural_width(self) -> int:
        return self._layout.natural_width()

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
                self.sprite_deselected.emit(path.stem)   # NEW

            self.count_changed.emit(self._count)
            self.sprite_clicked.emit(path)