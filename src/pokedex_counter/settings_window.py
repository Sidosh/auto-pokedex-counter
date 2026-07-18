"""Settings window shown alongside MainWindow - the counter window sits in
a stream layout, so no button/menu can live there without appearing on
stream; this window carries all the controls instead.

This is a dumb view: it holds no references to GameController/
DetectionService/CaptureService. All cross-object wiring happens in
app.py, matching the existing convention there.
"""

from PySide6.QtWidgets import QCheckBox, QFormLayout, QPushButton, QSpinBox, QVBoxLayout, QWidget

DEFAULT_SPRITES_PER_ROW = 10
DEFAULT_FONT_SIZE = 24


class SettingsWindow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pokedex Counter Settings")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setRange(1, 30)
        self.columns_spinbox.setValue(DEFAULT_SPRITES_PER_ROW)
        form.addRow("Sprites per row:", self.columns_spinbox)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 96)
        self.font_size_spinbox.setValue(DEFAULT_FONT_SIZE)
        form.addRow("Counter font size:", self.font_size_spinbox)

        self.compare_to_wr_checkbox = QCheckBox()
        form.addRow("Compare to WR?", self.compare_to_wr_checkbox)

        layout.addLayout(form)

        self.reset_button = QPushButton("Reset counter")
        layout.addWidget(self.reset_button)

        self.calibrate_button = QPushButton("Calibrate")
        layout.addWidget(self.calibrate_button)
