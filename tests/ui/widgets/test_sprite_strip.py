import pytest

from pokedex_counter.config import SPRITES_DIR
from pokedex_counter.ui.widgets.sprite_strip import SpriteStrip


@pytest.fixture
def sprite_strip(qtbot):
    strip = SpriteStrip(SPRITES_DIR)
    qtbot.addWidget(strip)
    return strip


def test_reset_deselects_everything_and_zeroes_the_count(sprite_strip):
    some_names = list(sprite_strip._labels_by_name)[:3]
    for name in some_names:
        sprite_strip.select_sprite(name)
    assert sprite_strip._count == 3

    deselected = []
    sprite_strip.sprite_deselected.connect(deselected.append)
    counts = []
    sprite_strip.count_changed.connect(counts.append)

    sprite_strip.reset()

    assert sprite_strip._count == 0
    assert set(deselected) == set(some_names)
    assert counts[-1] == 0
    assert all(not label._selected for label in sprite_strip._labels_by_name.values())


def test_reset_on_already_empty_strip_is_a_noop(sprite_strip):
    sprite_strip.reset()
    assert sprite_strip._count == 0
