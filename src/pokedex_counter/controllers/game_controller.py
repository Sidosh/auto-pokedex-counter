# core/controller.py
from PySide6.QtCore import QObject, Signal

class GameController(QObject):
    # (dex number, section it was found in). The section rides along because
    # the same dex number can be routed differently per section - notably as
    # a catch in one and an evolution in another - and the UI needs to know
    # which happened to color it (see roi_config.is_evolution).
    pokemon_found = Signal(str, int)
    count_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.found = set()
        self.count = 0
        # Current run's catches grouped by section, in catch order - same
        # {section_index: [dex, ...]} shape PB.json is saved in (see
        # services/pb_service.py). Kept in sync with `_current_section` via
        # on_section_changed, wired to DetectionService.section_changed in
        # app.py so section attribution always reflects what was active at
        # catch time, not whatever section the run is in later.
        self.section_catches: dict[int, list[str]] = {}
        self._current_section = 0

    def on_section_changed(self, section: int) -> None:
        self._current_section = section

    def on_detection(self, name: str):
        if name in self.found:
            return

        self.found.add(name)
        self.count += 1
        self.section_catches.setdefault(self._current_section, []).append(name)

        self.pokemon_found.emit(name, self._current_section)
        self.count_changed.emit(self.count)

    def forget(self, name: str) -> None:
        self.found.discard(name)
        for names in self.section_catches.values():
            if name in names:
                names.remove(name)
                break