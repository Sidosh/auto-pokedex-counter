import json

from pokedex_counter.config import WR_JSON_PATH


def load_wr_sections() -> dict[int, set[str]]:
    """Maps DetectionService section index -> dex numbers considered "on
    route" for that section, per WR.json. Missing/unreadable file means the
    feature is quietly unavailable (compare_to_wr just has nothing to mark).

    WR.json splits the endgame across keys "10" and "11", but
    DetectionService's last section (index 10) absorbs everything after the
    last trigger and never advances further - so "10" and "11" are merged
    into index 10 here to match.
    """
    if not WR_JSON_PATH.is_file():
        return {}

    try:
        with open(WR_JSON_PATH, encoding="utf-8") as f:
            raw: dict[str, list[str]] = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[wr_service] WARNING: failed to load '{WR_JSON_PATH}', compare-to-WR disabled: {e}")
        return {}

    sections: dict[int, set[str]] = {}
    for key, names in raw.items():
        index = min(int(key), 10)
        sections.setdefault(index, set()).update(names)

    return sections
