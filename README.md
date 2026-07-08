# Pokedex Counter

A small [PySide6](https://doc.qt.io/qtforpython-6/) overlay window for tracking your Pokédex progress live while streaming a Pokémon Red/Blue/Yellow playthrough from a Game Boy capture feed. It watches the video feed, recognizes catch, evolution and "give a nickname?" screens, and keeps a running count of the 151 Pokémon you've found — handy as an OBS window/source capture.

## Download (no Python required)

Grab the latest `PokedexCounter.exe` from the [Releases page](https://github.com/Sidosh/auto-pokedex-counter/releases) and run it. Windows only.

It expects a camera/capture device at index 2 (e.g. a capture card feeding your Game Boy or emulator video) — that's currently hardcoded, so if your device is on a different index you'll need to run from source (see below) with `camera_index` changed in `app.py`/`calibration_runner.py`.

### What happens on launch: calibration

Every time the app starts, it calibrates itself before the counter window opens:

1. You need to launch the OBS Virtual Camera
2. A small "Calibration" preview window pops up showing your camera feed.
3. Point the feed at the **Pokémon title screen** (the "Pokémon Blue Version" boot screen) — the app matches against that screen to figure out exactly where on your camera frame the catch/evolution/nickname regions are. This is necessary because everyone's camera framing and streaming layout is different.
4. Colored boxes on the preview show live match confidence for the three regions it's searching for. Once all three are found confidently and held steady for a moment, the preview closes automatically and the counter window opens.
5. Press `Esc` at any point to skip calibration — the app falls back to whatever positions worked last time instead.

A successful calibration is remembered for next launch (saved as a `roi_config.py` file next to the `.exe`), so you typically only need to re-do it if your camera framing changes.

## Setup (for development)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m pokedex_counter
```

## Test

```bash
pytest
```

## Build a standalone executable

```bash
python scripts/build.py
```

This produces `dist/PokedexCounter.exe` (bundled with `resources/`) using PyInstaller. Pushing a `v*` tag also builds and attaches this exe to a GitHub Release automatically (see `.github/workflows/release.yml`).

## Project structure

```text
src/pokedex_counter/
  __main__.py               Entry point (`python -m pokedex_counter`)
  app.py                     QApplication bootstrap and service wiring
  calibration_runner.py      Runs calibration on startup, persists locked ROIs
  roi_config.py               Per-Pokemon ROI mapping + ROI_CATCH/EVOLVE/TEXT
  roi_writer.py               Rewrites roi_config.py's ROI_* constants on disk
  config.py                   App-wide constants, resource paths
  main_window.py              Main window UI (sprite grid + counter)
  controllers/game_controller.py   Tracks which Pokemon have been found
  services/
    capture_service.py        Camera capture thread
    calibration_service.py    Live ROI calibration against the title screen
    detection_service.py      Per-frame catch/evolve/text detection
    template_service.py       Loads sprite template images
  vision/template_matching.py Multi-scale template matching helper
  ui/widgets/                 Sprite strip, flow layout, etc.
  resources/
    sprites/, sprites_background/   Per-Pokemon template images
    calibration/                    Title-screen reference crops
tests/                        pytest + pytest-qt tests
scripts/build.py              PyInstaller packaging script
```
