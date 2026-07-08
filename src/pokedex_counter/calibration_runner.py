import sys
from pathlib import Path

import cv2

from pokedex_counter.config import RESOURCES_DIR
from pokedex_counter.roi_writer import update_roi_constants
from pokedex_counter.services.calibration_service import CalibrationService

_FILENAMES = {"CATCH": "catch.png", "EVOLVE": "evolve.png", "TEXT": "text.png"}

_SEED_TEMPLATE = """ROI_CATCH = {catch}
ROI_EVOLVE = {evolve}
ROI_TEXT = {text}
"""


def _writable_roi_config_path() -> Path:
    """Where calibration persists locked ROIs for next launch.

    Source/dev runs write straight into the package's roi_config.py (the
    file `from pokedex_counter.roi_config import ...` reads). A frozen exe
    has no such writable file — its modules are baked into the bundle — so
    it gets its own roi_config.py next to the executable instead. Either
    way, calibrate_on_startup() also returns the locked ROIs so the current
    run doesn't depend on this write (or a re-import) succeeding.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "roi_config.py"
    return Path(__file__).resolve().parent / "roi_config.py"


def _ensure_seeded(config_path: Path) -> None:
    if config_path.exists():
        return

    from pokedex_counter.roi_config import ROI_CATCH, ROI_EVOLVE, ROI_TEXT

    config_path.write_text(_SEED_TEMPLATE.format(catch=ROI_CATCH, evolve=ROI_EVOLVE, text=ROI_TEXT))


def calibrate_on_startup(camera_index=2) -> dict[str, tuple[int, int, int, int]]:
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
        return {}

    print(f"[Calibration] Starting up — waiting to lock: {list(templates)}")
    locked = CalibrationService(camera_index=camera_index).run(templates)  # no timeout: waits as long as needed

    if not locked:
        print("[Calibration] Nothing locked, using existing ROI_* values.")
        return {}

    config_path = _writable_roi_config_path()
    try:
        _ensure_seeded(config_path)
        updated = update_roi_constants(config_path, locked)
        print(f"[Calibration] Updated {updated} in {config_path}")
    except OSError as exc:
        print(f"[Calibration] Could not persist calibrated ROIs to {config_path} ({exc}); using them for this session only.")

    return locked
