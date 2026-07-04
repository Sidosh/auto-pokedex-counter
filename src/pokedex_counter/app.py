"""Application bootstrap: creates the QApplication and shows the main window."""

import sys

from PySide6.QtWidgets import QApplication

from pokedex_counter.main_window import MainWindow


def run() -> int:
    """Create the QApplication, show the main window, and start the event loop."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()
