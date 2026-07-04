"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)

from pokedex_counter.config import APP_NAME, SPRITES_DIR
from pokedex_counter.ui.widgets.sprite_strip import SpriteStrip


class MainWindow(QMainWindow):
    """The application's main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(480, 320)

        self._build_ui()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.sprite_strip = SpriteStrip(SPRITES_DIR)

        layout.addWidget(QLabel("Sprites:"))
        layout.addWidget(self.sprite_strip)

        self.setCentralWidget(central_widget)