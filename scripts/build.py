"""Build a standalone executable using PyInstaller.

Usage:
    python scripts/build.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY_POINT = ROOT / "src" / "my_app" / "__main__.py"


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name",
            "MyDesktopApp",
            "--windowed",  # no console window (GUI app)
            "--onefile",  # single executable
            "--paths",
            str(ROOT / "src"),
            str(ENTRY_POINT),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
