from pathlib import Path

import pytest

from pokedex_counter.ui.widgets.clickable_label import ClickableLabel


@pytest.fixture
def label(qtbot):
    lbl = ClickableLabel(Path("42.png"))
    qtbot.addWidget(lbl)
    return lbl


def test_select_then_deselect_round_trip(label):
    assert not label._selected

    label.select()
    assert label._selected

    label.deselect()
    assert not label._selected


def test_deselect_is_a_noop_when_not_selected(label, qtbot):
    with qtbot.assertNotEmitted(label.clicked):
        label.deselect()

    assert not label._selected


def test_deselect_emits_clicked_with_the_path(label, qtbot):
    label.select()

    with qtbot.waitSignal(label.clicked, timeout=100) as blocker:
        label.deselect()

    assert blocker.args == [Path("42.png")]
