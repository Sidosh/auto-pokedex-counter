"""Main application window."""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
)

from pokedex_counter.config import APP_NAME, SPRITES_DIR
from pokedex_counter.ui.widgets.sprite_strip import SpriteStrip


class MainWindow(QMainWindow):
    """The application's main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(880, 880)

        self._build_ui()

        QTimer.singleShot(0, self._sync_height_to_width)

    def _build_ui(self) -> None:
        self._central_widget = QWidget()
        layout = QVBoxLayout(self._central_widget)

        self.sprite_strip = SpriteStrip(SPRITES_DIR)

        layout.addWidget(self.sprite_strip)

        self.setCentralWidget(self._central_widget)

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