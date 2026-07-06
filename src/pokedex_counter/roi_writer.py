import re
from pathlib import Path

_CONST_NAMES = {"CATCH": "ROI_CATCH", "EVOLVE": "ROI_EVOLVE", "TEXT": "ROI_TEXT"}


def update_roi_constants(config_path: Path, locked: dict[str, tuple[int, int, int, int]]) -> list[str]:
    text = config_path.read_text()
    updated = []

    for key, box in locked.items():
        const_name = _CONST_NAMES.get(key)
        if const_name is None:
            continue

        pattern = re.compile(rf"^{const_name}\s*=\s*\([^)]*\)", re.MULTILINE)
        replacement = f"{const_name} = {tuple(box)}"

        new_text, count = pattern.subn(replacement, text)
        if count == 0:
            print(f"[roi_writer] WARNING: could not find `{const_name} = (...)` in {config_path}, skipping")
            continue
        if count > 1:
            print(f"[roi_writer] WARNING: found {count} matches for `{const_name}` — updated all")

        text = new_text
        updated.append(const_name)

    config_path.write_text(text)
    return updated