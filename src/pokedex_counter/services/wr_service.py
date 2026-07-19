import json

from pokedex_counter.config import WR_JSON_PATH


def load_wr_sections() -> dict[int, set[str]]:
    """Maps DetectionService section index -> dex numbers considered "on
    route" for that section, per WR.json. Missing/unreadable file means the
    feature is quietly unavailable (compare_to_wr just has nothing to mark).

    WR.json's keys already line up 1:1 with DetectionService's section
    indices, including the dedicated evolution section at the end (see
    roi_config.py's CATCH_SECTIONS_RAW)."""
    if not WR_JSON_PATH.is_file():
        return {}

    try:
        with open(WR_JSON_PATH, encoding="utf-8") as f:
            raw: dict[str, list[str]] = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[wr_service] WARNING: failed to load '{WR_JSON_PATH}', compare-to-WR disabled: {e}")
        return {}

    return {int(key): set(names) for key, names in raw.items()}
