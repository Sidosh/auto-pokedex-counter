"""App-wide constants and settings."""

from pathlib import Path

APP_NAME = "Pokedex Counter"
APP_VERSION = "0.1.0"
ORGANIZATION_NAME = "MyOrg"

# Directory containing sprite images shown in the main window.
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
SPRITES_DIR = RESOURCES_DIR / "sprites"
SPRITES_BG_DIR = RESOURCES_DIR / "sprites_background"