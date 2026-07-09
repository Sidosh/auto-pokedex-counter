from pathlib import Path

import cv2
import numpy as np
import pytest

from pokedex_counter.config import FRAME_SIZE, SPRITES_BG_DIR
from pokedex_counter.roi_config import build_detection_entries
from pokedex_counter.services.detection_service import DetectionService
from pokedex_counter.services.template_service import TemplateService

DETECTION_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "detection"

# (calibration_fixture, label, detection_fixture, expected_name, expected_section)
# expected_section is where `expected_name` actually lives in CATCH_SECTIONS,
# since detection is only active for the current section - see
# _prime_to_section below.
DETECTION_CASES = [
    ("calibration_01.png", "catch", "catch_01.png", "97", 1),
    ("calibration_01.png", "evolve", "evolve_01.png", "80", 10),
    ("calibration_01.png", "text", "text_01.png", "35", 9),
    ("calibration_02.png", "catch", "catch_02.png", "97", 1),
    ("calibration_02.png", "evolve", "evolve_02.png", "80", 10),
    ("calibration_02.png", "text", "text_02.png", "35", 9),
]


@pytest.fixture(scope="module")
def sprite_templates():
    return TemplateService(Path(SPRITES_BG_DIR)).templates


def _roi_templates_for(calibration_fixture, sprite_templates, calibrated_rois):
    rois = calibrated_rois[calibration_fixture]
    locked = {"CATCH": rois["catch"], "EVOLVE": rois["evolve"], "TEXT": rois["text"]}
    return build_detection_entries(sprite_templates, locked)


def _prime_to_section(detector, section_index):
    """Simulate the run having already progressed to `section_index`, by
    marking every earlier section's trigger as already detected.
    DetectionService only matches templates in its current active section
    (see roi_config.py's CATCH_SECTIONS/SECTION_TRIGGERS), so a cold
    detector can't see a later section's Pokemon in isolation the way
    these fixtures test them."""
    detector._detected.update(t for t in detector._section_triggers[:section_index] if t is not None)


@pytest.mark.parametrize(
    "calibration_fixture, label, detection_fixture, expected_name, expected_section", DETECTION_CASES
)
def test_calibrated_roi_detects_expected_pokemon(
    sprite_templates, calibrated_rois, calibration_fixture, label, detection_fixture, expected_name, expected_section
):
    roi_templates = _roi_templates_for(calibration_fixture, sprite_templates, calibrated_rois)

    detector = DetectionService(roi_templates)
    _prime_to_section(detector, expected_section)
    detections = []
    detector.detection.connect(detections.append)

    frame = cv2.imread(str(DETECTION_FIXTURES_DIR / detection_fixture))
    assert frame is not None, f"Could not load image: {detection_fixture}"
    detector.process_frame(cv2.flip(frame, 1))

    assert detections == [expected_name], (
        f"{calibration_fixture} -> {detection_fixture} ({label}): "
        f"expected detection {expected_name!r}, got {detections}"
    )


def test_repeated_frames_detect_only_once_until_forgotten(sprite_templates, calibrated_rois):
    roi_templates = _roi_templates_for("calibration_01.png", sprite_templates, calibrated_rois)

    detector = DetectionService(roi_templates)
    _prime_to_section(detector, 1)  # "97" lives in section 1
    detections = []
    detector.detection.connect(detections.append)

    frame = cv2.imread(str(DETECTION_FIXTURES_DIR / "catch_01.png"))
    flipped = cv2.flip(frame, 1)

    # Same screen held across many frames (e.g. player hasn't pressed a
    # button yet) must only fire the signal once, not once per frame.
    for _ in range(5):
        detector.process_frame(flipped)
    assert detections == ["97"]

    # A frame with nothing recognizable must not re-trigger it either.
    detector.process_frame(np.zeros_like(flipped))
    assert detections == ["97"]

    # Only forgetting it (manual "unclick" in the UI) allows re-detection.
    detector.forget("97")
    detector.process_frame(flipped)
    assert detections == ["97", "97"]


def _pattern(seed, size=20):
    return np.random.RandomState(seed).randint(0, 256, (size, size), dtype=np.uint8)


def _frame_with_pattern_at(roi, pattern):
    """Build a frame containing `pattern` exactly at `roi`. The result is
    pre-flipped so passing it to process_frame (which flips once) lands
    the pattern at `roi` in the coordinates DetectionService crops from."""
    width, height = FRAME_SIZE
    frame = np.full((height, width, 3), 127, dtype=np.uint8)
    x, y, w, h = roi
    for channel in range(3):
        frame[y:y + h, x:x + w, channel] = pattern
    return cv2.flip(frame, 1)


def test_entries_outside_active_section_are_excluded_until_trigger_fires():
    roi = (0, 0, 20, 20)
    name_a, name_b = "A", "B"
    roi_templates = [(name_a, roi, _pattern(1), 0), (name_b, roi, _pattern(2), 1)]

    detector = DetectionService(roi_templates)
    detector._section_triggers = [name_a, None]  # detecting "A" advances to section 1
    detections = []
    detector.detection.connect(detections.append)

    frame_b = _frame_with_pattern_at(roi, _pattern(2))  # exact match for "B"

    # Fresh detector starts on section 0; "B" belongs to section 1 and must
    # not be considered at all, even though it's a perfect pixel match.
    detector.process_frame(frame_b)
    assert detections == []

    # Detecting "A" (section 0's trigger) advances to section 1, so the
    # same frame is now detected as "B".
    detector.process_frame(_frame_with_pattern_at(roi, _pattern(1)))
    assert detections == [name_a]

    detector.process_frame(frame_b)
    assert detections == [name_a, name_b]


def test_forgetting_the_trigger_rolls_back_the_active_section():
    roi = (0, 0, 20, 20)
    name_a, name_b = "A", "B"
    roi_templates = [(name_a, roi, _pattern(1), 0), (name_b, roi, _pattern(2), 1)]

    detector = DetectionService(roi_templates)
    detector._section_triggers = [name_a, None]
    detections = []
    detector.detection.connect(detections.append)

    frame_a = _frame_with_pattern_at(roi, _pattern(1))
    frame_b = _frame_with_pattern_at(roi, _pattern(2))

    detector.process_frame(frame_a)
    detector.process_frame(frame_b)
    assert detections == [name_a, name_b]

    # Undo both (e.g. the player manually un-clicks a misdetection). "A"
    # being forgotten must roll the active section back to 0, so "B" isn't
    # matched again even though its template is still a perfect fit.
    detector.forget(name_a)
    detector.forget(name_b)
    detector.process_frame(frame_b)
    assert detections == [name_a, name_b]


def test_update_rois_rebuilds_groups_without_touching_detected():
    roi = (0, 0, 20, 20)
    detector = DetectionService([("A", roi, _pattern(1), 0)])
    detector._detected.add("A")

    new_roi = (0, 0, 25, 25)
    detector.update_rois([("B", new_roi, _pattern(2), 0)])

    assert "A" in detector._detected  # mid-run progress survives recalibration
    assert [roi for roi, _entries in detector._roi_groups] == [new_roi]
    names_in_group = {name for name, _template, _section in detector._roi_groups[0][1]}
    assert names_in_group == {"B"}


def test_update_rois_new_templates_are_matched_immediately():
    roi = (0, 0, 20, 20)
    detector = DetectionService([("A", roi, _pattern(1), 0)])
    detections = []
    detector.detection.connect(detections.append)

    detector.update_rois([("B", roi, _pattern(2), 0)])
    detector.process_frame(_frame_with_pattern_at(roi, _pattern(2)))

    assert detections == ["B"]
