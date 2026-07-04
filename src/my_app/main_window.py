"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from my_app.config import APP_NAME


class MainWindow(QMainWindow):
    """The application's main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(480, 320)

        self._click_count = 0

        self._build_ui()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Hello, world! 👋")
        self.label.setStyleSheet("font-size: 20px;")

        self.button = QPushButton("Click me")
        self.button.clicked.connect(self._on_button_clicked)

        layout.addStretch()
        layout.addWidget(self.label, alignment=self.label.alignment())
        layout.addWidget(self.button)
        layout.addStretch()

        self.setCentralWidget(central_widget)

    def _on_button_clicked(self) -> None:
        self._click_count += 1
        self.label.setText(f"Clicked {self._click_count} time(s)")
