from pathlib import Path

import cv2

from pokedex_counter.config import RESOURCES_DIR
from pokedex_counter.roi_writer import update_roi_constants
from pokedex_counter.services.calibration_service import CalibrationService

_FILENAMES = {"CATCH": "catch.png", "EVOLVE": "evolve.png", "TEXT": "text.png"}


def calibrate_on_startup(camera_index=2) -> None:
    calibration_dir = RESOURCES_DIR / "calibration"

    templates = {}
    for name, filename in _FILENAMES.items():
        path = calibration_dir / filename
        img = cv2.imread(str(path))
        if img is None:
            print(f"[Calibration] ERROR: could not load reference image {path}, skipping {name}")
            continue
        templates[name] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if not templates:
        print("[Calibration] No reference images found, skipping calibration.")
        return

    print(f"[Calibration] Starting up — waiting to lock: {list(templates)}")
    locked = CalibrationService(camera_index=camera_index).run(templates)  # no timeout: waits as long as needed

    if not locked:
        print("[Calibration] Nothing locked, roi_config.py left unchanged.")
        return

    config_path = Path(__file__).resolve().parent / "roi_config.py"
    updated = update_roi_constants(config_path, locked)
    print(f"[Calibration] Updated {updated} in {config_path}")