"""Shared pytest fixtures. pytest-qt provides the `qtbot` fixture automatically."""

import pytest

from my_app.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    return window
