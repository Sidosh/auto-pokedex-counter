# My Desktop App

A desktop application built with [PySide6](https://doc.qt.io/qtforpython-6/) (Qt for Python).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m my_app
```

## Test

```bash
pytest
```

## Build a standalone executable

```bash
python scripts/build.py
```

This produces a single executable in `dist/` using PyInstaller.

## Project structure

```
src/my_app/          Application source code
  __main__.py         Entry point (`python -m my_app`)
  app.py              QApplication bootstrap
  main_window.py       Main window UI
  config.py           App-wide constants
  ui/                 Additional widgets/views
  models/             Business logic, data models (no Qt imports)
  controllers/        Glue between UI and models
  resources/          Icons, images, .qrc files
tests/                pytest + pytest-qt tests
scripts/build.py       PyInstaller packaging script
```
