import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QLabel, QWidget

from pokedex_counter.ui.widgets.flow_layout import FlowLayout


@pytest.fixture
def container(qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)
    layout = FlowLayout(widget)
    widget.setLayout(layout)
    return widget, layout


def _add_fixed_size_labels(layout, count, size=20):
    for _ in range(count):
        label = QLabel()
        label.setFixedSize(size, size)
        layout.addWidget(label)


def test_default_mode_wraps_by_width(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 5, size=20)

    layout.setGeometry(QRect(0, 0, 50, 0))  # room for ~2 per row before wrapping

    rows = {layout.itemAt(i).geometry().y() for i in range(5)}
    assert len(rows) > 1


def test_set_columns_wraps_every_n_items_regardless_of_width(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 6, size=20)

    layout.set_columns(3)
    layout.setGeometry(QRect(0, 0, 1000, 0))  # would NOT wrap by width alone

    xs = [layout.itemAt(i).geometry().x() for i in range(6)]
    ys = [layout.itemAt(i).geometry().y() for i in range(6)]

    assert ys[0] == ys[1] == ys[2]
    assert ys[3] == ys[4] == ys[5]
    assert ys[3] > ys[0]
    assert xs[0] < xs[1] < xs[2]
    assert xs[3] == xs[0]


def test_set_columns_none_reverts_to_width_based_wrapping(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 6, size=20)

    layout.set_columns(3)
    layout.set_columns(None)
    layout.setGeometry(QRect(0, 0, 1000, 0))

    rows = {layout.itemAt(i).geometry().y() for i in range(6)}
    assert len(rows) == 1


def test_natural_width_is_zero_without_a_fixed_column_count(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 6, size=20)

    assert layout.natural_width() == 0


def test_natural_width_fits_exactly_n_items_with_no_spacing(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 6, size=20)

    layout.set_columns(3)

    assert layout.natural_width() == 3 * 20


def test_natural_width_accounts_for_spacing_and_margins():
    widget = QWidget()
    layout = FlowLayout(widget, margin=5, spacing=2)
    widget.setLayout(layout)
    _add_fixed_size_labels(layout, 6, size=20)

    layout.set_columns(3)

    # 3 items * 20px + 2 gaps * 2px spacing + 5px margin on each side
    assert layout.natural_width() == 3 * 20 + 2 * 2 + 2 * 5


def test_natural_width_caps_at_item_count_when_fewer_than_columns(container):
    _widget, layout = container
    _add_fixed_size_labels(layout, 2, size=20)

    layout.set_columns(5)

    assert layout.natural_width() == 2 * 20
