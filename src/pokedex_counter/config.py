"""App-wide constants and settings."""

import sys
from pathlib import Path

APP_NAME = "Pokedex Counter"
APP_VERSION = "0.1.0"
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

FRAME_SIZE = (640, 360)