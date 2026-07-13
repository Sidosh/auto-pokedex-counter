"""App-wide constants and settings."""

import sys
from pathlib import Path

APP_NAME = "Pokedex Counter"
APP_VERSION = "0.3.1"
ORGANIZATION_NAME = "MyOrg"

# When frozen by PyInstaller, data files added via --add-data are extracted
# to sys._MEIPASS (a temp dir) instead of living next to this module.
if getattr(sys, "frozen", False):
    _PACKAGE_DIR = Path(sys._MEIPASS)
else:
    _PACKAGE_DIR = Path(__file__).resolve().parent

# Directory containing sprite images shown in the main window.
RESOURCES_DIR = _PACKAGE_DIR / "resources"
SPRITES_DIR = RESOURCES_DIR / "sprites"
SPRITES_BG_DIR = RESOURCES_DIR / "sprites_background"
FONTS_DIR = RESOURCES_DIR / "fonts"

THRESHOLD = 0.85

# Minimum gap (0-255 grayscale units) required between adjacent k-means
# shade-cluster centers for canonicalize_shades() to trust the clustering.
# Below this, treat the crop as having no reliable 4-shade structure
# (blank/transition frame) rather than rank-remapping noise into a
# fabricated full-contrast pattern.
MIN_SHADE_SEPARATION = 15.0

# Extra pixels of padding added around each calibrated ROI before matching,
# so cv2.matchTemplate can search for the best-aligned position instead of
# assuming the calibrated position is exactly right. Different capture
# sessions (even against the same physical setup) can drift by a pixel or
# two - sprite icons are blocky enough to tolerate that, but fine text
# glyphs are not, so this margin matters most for ROI_TEXT.
ROI_SEARCH_MARGIN = 4

FRAME_SIZE = (640, 360)