# core/controller.py
from PySide6.QtCore import QObject, Signal

class GameController(QObject):
    pokemon_found = Signal(str)
    count_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.found = set()
        self.count = 0

    def on_detection(self, name: str):
        if name in self.found:
            return

        self.found.add(name)
        self.count += 1

        self.pokemon_found.emit(name)
        self.count_changed.emit(self.count)

    def forget(self, name: str) -> None:
        self.found.discard(name)