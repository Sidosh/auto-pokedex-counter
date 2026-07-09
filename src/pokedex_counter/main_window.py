"""Main application window."""

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QResizeEvent, QFontDatabase, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from pokedex_counter.config import APP_NAME, FONTS_DIR, SPRITES_DIR
from pokedex_counter.ui.widgets.sprite_strip import SpriteStrip

DEFAULT_COUNTER_FONT_SIZE = 24


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(300, 600)

        self._build_ui()

        QTimer.singleShot(0, self._sync_height_to_width)

    def _build_ui(self) -> None:
        self._central_widget = QWidget()
        layout = QVBoxLayout(self._central_widget)

        self.sprite_strip = SpriteStrip(SPRITES_DIR)

        layout.addWidget(self.sprite_strip)

        self.sprite_strip.count_changed.connect(self._update_counter)
        self.counter_label = QLabel("0")
        self.counter_label.setStyleSheet("margin-top: 10px;")
        font_id = QFontDatabase.addApplicationFont(str(FONTS_DIR / "Pokemon Solid.ttf"))
        families = QFontDatabase.applicationFontFamilies(font_id)
        font = QFont(families[0]) if families else self.counter_label.font()
        font.setPointSize(DEFAULT_COUNTER_FONT_SIZE)
        self.counter_label.setFont(font)

        layout.addWidget(self.counter_label)

        self.setCentralWidget(self._central_widget)

    def bind_controller(self, controller):
        controller.count_changed.connect(self._update_counter)

    def _update_counter(self, value: int):
        self.counter_label.setText(f"{value} caught")

    def set_sprites_per_row(self, columns: int) -> None:
        self.sprite_strip.set_columns(columns)

        width = self.sprite_strip.natural_width()
        if width > 0:
            margins = self._central_widget.layout().contentsMargins()
            self.setFixedWidth(width + margins.left() + margins.right())

        QTimer.singleShot(0, self._sync_height_to_width)

    def set_counter_font_size(self, points: int) -> None:
        font = self.counter_label.font()
        font.setPointSize(points)
        self.counter_label.setFont(font)
        QTimer.singleShot(0, self._sync_height_to_width)

    def resizeEvent(self, event: QResizeEvent) -> None:
        QTimer.singleShot(0, self._sync_height_to_width)

    def _sync_height_to_width(self) -> None:
        layout = self._central_widget.layout()
        content_width = self._central_widget.width()
        needed_content_height = layout.totalHeightForWidth(content_width)

        chrome_height = self.frameGeometry().height() - self.geometry().height()
        target_height = needed_content_height

        if target_height != self.height():
            self.resize(self.width(), target_height)