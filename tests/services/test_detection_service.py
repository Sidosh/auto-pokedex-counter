from pathlib import Path

import cv2
import pytest

from pokedex_counter.config import SPRITES_BG_DIR
from pokedex_counter.roi_config import ROI_CATCH, ROI_CONFIG, ROI_EVOLVE, ROI_TEXT
from pokedex_counter.services.detection_service import DetectionService
from pokedex_counter.services.template_service import TemplateService

DETECTION_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "detection"

_LABEL_BY_ROI_ID = {id(ROI_CATCH): "catch", id(ROI_EVOLVE): "evolve", id(ROI_TEXT): "text"}

DETECTION_CASES = [
    ("calibration_01.png", "catch", "catch_01.png", "97"),
    ("calibration_01.png", "evolve", "evolve_01.png", "80"),
    ("calibration_01.png", "text", "text_01.png", "35"),
    ("calibration_02.png", "catch", "catch_02.png", "97"),
    ("calibration_02.png", "evolve", "evolve_02.png", "80"),
    ("calibration_02.png", "text", "text_02.png", "35"),
]


@pytest.fixture(scope="module")
def sprite_templates():
    return TemplateService(Path(SPRITES_BG_DIR)).templates


@pytest.mark.parametrize("calibration_fixture, label, detection_fixture, expected_name", DETECTION_CASES)
def test_calibrated_roi_detects_expected_pokemon(
    sprite_templates, calibrated_rois, calibration_fixture, label, detection_fixture, expected_name
):
    rois = calibrated_rois[calibration_fixture]
    roi_templates = [
        (name, rois[_LABEL_BY_ROI_ID[id(roi)]], sprite_templates[name])
        for name, roi in ROI_CONFIG
    ]

    detector = DetectionService(roi_templates)
    detections = []
    detector.detection.connect(detections.append)

    frame = cv2.imread(str(DETECTION_FIXTURES_DIR / detection_fixture))
    assert frame is not None, f"Could not load image: {detection_fixture}"
    detector.process_frame(cv2.flip(frame, 1))

    assert detections == [expected_name], (
        f"{calibration_fixture} -> {detection_fixture} ({label}): "
        f"expected detection {expected_name!r}, got {detections}"
    )
