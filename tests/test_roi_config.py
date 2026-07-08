"""Locks in resolve_roi_templates()'s contract: calibrate_on_startup()'s
locked ROIs must apply in-memory for this session regardless of whether
they got persisted to disk (see test_calibration_runner.py and
test_roi_writer.py for the persistence side of that).
"""

from collections import defaultdict

from pokedex_counter.roi_config import (
    ROI_CATCH,
    ROI_CONFIG,
    ROI_EVOLVE,
    ROI_TEXT,
    resolve_roi_templates,
)


def _fake_templates():
    return defaultdict(lambda: "template-stub")


def test_falls_back_to_static_rois_when_nothing_locked():
    result = resolve_roi_templates(_fake_templates(), locked=None)

    assert len(result) == len(ROI_CONFIG)
    rois_used = {roi for _, roi, _ in result}
    assert rois_used == {ROI_CATCH, ROI_EVOLVE, ROI_TEXT}


def test_applies_locked_rois_in_place_of_static_ones():
    locked = {"CATCH": (1, 1, 1, 1), "EVOLVE": (2, 2, 2, 2), "TEXT": (3, 3, 3, 3)}

    result = resolve_roi_templates(_fake_templates(), locked)

    rois_used = {roi for _, roi, _ in result}
    assert rois_used == {(1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3)}


def test_partial_lock_only_overrides_given_labels():
    locked = {"EVOLVE": (9, 9, 9, 9)}

    result = resolve_roi_templates(_fake_templates(), locked)

    rois_used = {roi for _, roi, _ in result}
    assert rois_used == {ROI_CATCH, (9, 9, 9, 9), ROI_TEXT}


def test_preserves_roi_config_order_and_names():
    result = resolve_roi_templates(_fake_templates(), locked=None)

    assert [name for name, _, _ in result] == [name for name, _ in ROI_CONFIG]
