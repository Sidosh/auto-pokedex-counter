"""Locks in build_detection_entries()'s contract: calibrate_on_startup()'s
locked ROIs must apply in-memory for this session regardless of whether
they got persisted to disk (see test_calibration_runner.py and
test_roi_writer.py for the persistence side of that).

Also guards CATCH_SECTIONS_RAW - the hand-authored catch route - against
transcription mistakes: every entry must resolve to a real sprite
template, and every dex number needs to be detectable somewhere.
"""

from collections import defaultdict
from pathlib import Path

from pokedex_counter.config import SPRITES_BG_DIR
from pokedex_counter.roi_config import (
    CATCH_SECTIONS,
    ROI_CATCH,
    ROI_EVOLVE,
    ROI_TEXT,
    SECTION_TRIGGERS,
    build_detection_entries,
)
from pokedex_counter.services.template_service import TemplateService


def _fake_templates():
    return defaultdict(lambda: "template-stub")


def test_falls_back_to_static_rois_when_nothing_locked():
    result = build_detection_entries(_fake_templates(), locked=None)

    assert len(result) == sum(len(section) for section in CATCH_SECTIONS)
    rois_used = {roi for _, roi, _, _ in result}
    assert rois_used == {ROI_CATCH, ROI_EVOLVE, ROI_TEXT}


def test_applies_locked_rois_in_place_of_static_ones():
    locked = {"CATCH": (1, 1, 1, 1), "EVOLVE": (2, 2, 2, 2), "TEXT": (3, 3, 3, 3)}

    result = build_detection_entries(_fake_templates(), locked)

    rois_used = {roi for _, roi, _, _ in result}
    assert rois_used == {(1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3)}


def test_partial_lock_only_overrides_given_labels():
    locked = {"EVOLVE": (9, 9, 9, 9)}

    result = build_detection_entries(_fake_templates(), locked)

    rois_used = {roi for _, roi, _, _ in result}
    assert rois_used == {ROI_CATCH, (9, 9, 9, 9), ROI_TEXT}


def test_preserves_section_order_and_tags_each_entry_with_its_section():
    result = build_detection_entries(_fake_templates(), locked=None)

    expected = [
        (name, section_index)
        for section_index, section in enumerate(CATCH_SECTIONS)
        for name, _roi_label in section
    ]
    assert [(name, section_index) for name, _roi, _template, section_index in result] == expected


def test_every_dex_number_has_at_least_one_detection_path():
    covered = {name for section in CATCH_SECTIONS for name, _roi_label in section}
    all_dex_numbers = {str(i) for i in range(1, 152)}
    assert all_dex_numbers - covered == set()


def test_section_triggers_are_members_of_their_own_section():
    for section_index, trigger in enumerate(SECTION_TRIGGERS):
        if trigger is None:
            continue
        names_in_section = {name for name, _roi_label in CATCH_SECTIONS[section_index]}
        assert trigger in names_in_section


def test_every_entry_resolves_to_a_real_sprite_template():
    templates = TemplateService(Path(SPRITES_BG_DIR)).templates

    build_detection_entries(templates, locked=None)  # raises KeyError on a typo'd dex number
