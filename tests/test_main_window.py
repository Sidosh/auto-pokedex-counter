from PySide6.QtCore import Qt


def test_window_title(main_window):
    assert main_window.windowTitle() == "My Desktop App"


def test_button_click_updates_label(qtbot, main_window):
    qtbot.mouseClick(main_window.button, Qt.MouseButton.LeftButton)
    assert "Clicked 1 time(s)" in main_window.label.text()
