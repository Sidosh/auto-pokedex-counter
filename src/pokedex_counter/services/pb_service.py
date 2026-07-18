import json

from pokedex_counter.config import PB_JSON_PATH


def save_pb(section_catches: dict[int, list[str]]) -> None:
    """Writes a completed run's catches to PB.json, grouped by section (in
    catch order) in the same {section_index: [dex, ...]} shape as WR.json."""
    data = {str(section): names for section, names in sorted(section_catches.items())}

    PB_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PB_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[pb_service] Saved personal best to {PB_JSON_PATH}")
