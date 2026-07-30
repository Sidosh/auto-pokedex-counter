"""run() itself needs a camera and a QApplication, so only the wiring
that's been hoisted out of it is exercised here - for the bonus highlight
that's the whole app-side contract: the checkbox drives the sprite strip,
and the state it was restored in is applied at startup rather than only on
the first toggle.
"""

import pytest

from pokedex_counter.app import wire_bonus_highlight
from pokedex_counter.config import SPRITES_DIR
from pokedex_counter.settings_window import SettingsWindow
from pokedex_counter.ui.widgets.sprite_strip import SpriteStrip

BONUSES = {"4"}


@pytest.fixture
def wired(qtbot):
    settings = SettingsWindow()
    strip = SpriteStrip(SPRITES_DIR)
    qtbot.addWidget(settings)
    qtbot.addWidget(strip)
    return settings, strip


def test_checking_the_box_highlights_bonuses(wired):
    settings, strip = wired
    wire_bonus_highlight(settings, strip, BONUSES)

    settings.highlight_bonuses_checkbox.setChecked(True)

    assert strip._bonus_names == BONUSES


def test_unchecking_the_box_turns_highlighting_off(wired):
    settings, strip = wired
    wire_bonus_highlight(settings, strip, BONUSES)
    settings.highlight_bonuses_checkbox.setChecked(True)

    settings.highlight_bonuses_checkbox.setChecked(False)

    assert strip._bonus_names == set()


def test_a_restored_checked_setting_applies_without_a_toggle(wired):
    """app.py restores the checkbox from QSettings before wiring it, so a
    session that had the setting on must come up highlighting already -
    waiting for a toggle would silently lose the preference."""
    settings, strip = wired
    settings.highlight_bonuses_checkbox.setChecked(True)  # as restored from QSettings

    wire_bonus_highlight(settings, strip, BONUSES)

    assert strip._bonus_names == BONUSES


def test_starts_off_when_the_setting_is_off(wired):
    settings, strip = wired

    wire_bonus_highlight(settings, strip, BONUSES)

    assert strip._bonus_names == set()
