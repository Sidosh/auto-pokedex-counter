"""Build a standalone executable using PyInstaller.

Usage:
    python scripts/build.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY_POINT = ROOT / "src" / "pokedex_counter" / "__main__.py"
RESOURCES_DIR = ROOT / "src" / "pokedex_counter" / "resources"


def main() -> None:
    # DEST is "resources" so it lands at sys._MEIPASS/resources at runtime,
    # matching config.py's frozen-mode RESOURCES_DIR resolution.
    add_data = f"{RESOURCES_DIR}{os.pathsep}resources"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name",
            "PokedexCounter",
            "--windowed",  # no console window (GUI app)
            "--onefile",  # single downloadable executable
            "--paths",
            str(ROOT / "src"),
            "--add-data",
            add_data,
            str(ENTRY_POINT),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
