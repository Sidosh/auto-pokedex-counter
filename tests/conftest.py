"""Shared pytest fixtures. pytest-qt provides the `qtbot` fixture automatically."""

import pytest

from pokedex_counter.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    return window
