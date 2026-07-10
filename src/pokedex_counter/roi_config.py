from pathlib import Path

# ROI_CATCH/ROI_EVOLVE/ROI_TEXT live in roi_calibration.py, a sibling module
# that's gitignored (see .gitignore) rather than committed - it holds this
# machine's camera calibration, which is personal/local and shouldn't show
# up as a diff every time this app is recalibrated. calibration_runner.py's
# run_calibration() rewrites that file in place via roi_writer.py.
#
# A fresh checkout won't have it yet - seed it with sane defaults the first
# time the import fails, then retry. When frozen, roi_calibration.py is
# baked into the PyInstaller bundle (it exists on disk at build time) and
# the import always succeeds, so this fallback only ever runs for a
# from-source checkout that's never been calibrated.
try:
    from pokedex_counter.roi_calibration import ROI_CATCH, ROI_EVOLVE, ROI_TEXT
except ImportError:
    _CALIBRATION_PATH = Path(__file__).resolve().parent / "roi_calibration.py"
    _CALIBRATION_PATH.write_text(
        "ROI_CATCH = (383, 35, 127, 127)\n"
        "ROI_EVOLVE = (275, 54, 126, 126)\n"
        "ROI_TEXT = (367, 273, 140, 50)\n"
    )
    from pokedex_counter.roi_calibration import ROI_CATCH, ROI_EVOLVE, ROI_TEXT

# Dex numbers whose "obtained" event is only ever confirmed via a name-text
# banner (trade evolutions etc.) rather than a sprite match against
# ROI_CATCH/ROI_EVOLVE.
TEXT_NAMES = {"33", "35", "63", "127", "131", "133", "137", "138", "142", "147"}

# Dex numbers that have an ROI_EVOLVE screen event (something evolves into
# them). Used to sweep any evolution not explicitly routed into a section
# below into the final section - see build_catch_sections().
EVOLVE_NAMES = {
    "3", "5", "6", "8", "9", "12", "14", "15", "18", "20", "24", "26", "28",
    "30", "31", "34", "36", "38", "40", "42", "44", "45", "47", "49", "51",
    "53", "55", "57", "59", "61", "62", "64", "67", "70", "71", "73", "75",
    "78", "80", "85", "87", "89", "91", "93", "97", "99", "101", "103",
    "105", "112", "117", "119", "121", "130", "134", "135", "136", "139",
    "141", "148",
}

# Hand-authored catch route: this specific playthrough's actual order,
# which does NOT follow ascending dex-number order (some Pokemon are only
# reachable well out of dex order, or via a detour). Detection only looks
# for the Pokemon in the currently active section (see DetectionService);
# a section's LAST entry is the trigger that advances to the next section.
# Order otherwise within a section doesn't matter. A dex number may repeat
# across sections if it can legitimately be caught in more than one of
# them.
CATCH_SECTIONS_RAW: list[list[str]] = [
    ["1", "16", "10", "51", "46", "29", "32", "102", "23", "122"],
    ["76", "97", "42", "28", "47", "64", "82", "40", "128", "113", "101",
     "85", "49", "26", "65", "112", "105", "150", "115"],
    ["82", "90", "54", "55", "42", "98", "99", "86", "87", "120", "129", "144"],
    ["66", "67", "74", "75", "42", "105", "49", "41", "95", "67", "68", "123"],
    ["21", "96", "27", "107", "58", "50", "109", "146", "48"],
    ["92", "126", "94", "22", "37", "19", "20", "17", "72", "4", "114"],
    ["21", "19", "84", "20", "111", "11", "140", "116", "149", "143", "151"],
    ["118", "39", "104", "47", "103", "30", "31", "43"],
    ["25", "81", "26", "100", "145", "83", "106", "7"],
    ["33", "35", "63", "127", "137", "147", "69", "56", "2", "131", "13"],
    ["138", "142", "133", "124", "132", "52", "77", "88", "89", "110", "125",
     "60", "79", "108"],
]

# Within these sections, these dex numbers refer to their ROI_EVOLVE event
# rather than the default CATCH/TEXT one.
SECTION_EVOLVE_OVERRIDES: dict[int, set[str]] = {
    7: {"30", "31", "47", "103"},  # section 8 (0-indexed 7)
}

# The dex number whose detection advances to the next section. The final
# section has none - there's nothing left to advance to.
SECTION_TRIGGERS: list[str | None] = [
    names[-1] if idx < len(CATCH_SECTIONS_RAW) - 1 else None
    for idx, names in enumerate(CATCH_SECTIONS_RAW)
]


def _entry_type(section_index: int, name: str) -> str:
    if name in SECTION_EVOLVE_OVERRIDES.get(section_index, ()):
        return "EVOLVE"
    if name in TEXT_NAMES:
        return "TEXT"
    return "CATCH"


def build_catch_sections() -> list[list[tuple[str, str]]]:
    """Expand CATCH_SECTIONS_RAW into (name, roi_label) pairs, then sweep
    every EVOLVE-type dex number not already placed in some section onto
    the end of the final section - evolutions not explicitly routed
    earlier all get caught up in one pass at the end of the run."""
    sections = [
        [(name, _entry_type(idx, name)) for name in names]
        for idx, names in enumerate(CATCH_SECTIONS_RAW)
    ]
    placed_evolves = {name for section in sections for name, rtype in section if rtype == "EVOLVE"}
    sections[-1] += [(name, "EVOLVE") for name in sorted(EVOLVE_NAMES - placed_evolves, key=int)]
    return sections


CATCH_SECTIONS: list[list[tuple[str, str]]] = build_catch_sections()


def build_detection_entries(templates: dict, locked: dict[str, tuple[int, int, int, int]] | None = None):
    """Build (name, roi, template, section_index) quadruples from
    CATCH_SECTIONS, substituting freshly calibrated boxes (as returned by
    run_calibration) for ROI_CATCH/ROI_EVOLVE/ROI_TEXT in-memory for
    this session.

    run_calibration() persists locked ROIs back into this file on a
    best-effort basis (e.g. it can't when frozen into an exe), but this app
    run must use them regardless of whether that write succeeded - hence
    applying `locked` here instead of relying on re-importing this module.
    """
    locked = locked or {}
    effective = {
        "CATCH": locked.get("CATCH", ROI_CATCH),
        "EVOLVE": locked.get("EVOLVE", ROI_EVOLVE),
        "TEXT": locked.get("TEXT", ROI_TEXT),
    }
    return [
        (name, effective[roi_label], templates[name], section_index)
        for section_index, section in enumerate(CATCH_SECTIONS)
        for name, roi_label in section
    ]
