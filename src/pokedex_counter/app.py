from pathlib import Path
from PySide6.QtWidgets import QApplication

from pokedex_counter.config import SPRITES_BG_DIR
from pokedex_counter.controllers.game_controller import GameController
from pokedex_counter.main_window import MainWindow
from pokedex_counter.roi_config import ROI_CONFIG
from pokedex_counter.services.capture_service import CaptureService
from pokedex_counter.services.detection_service import DetectionService
from pokedex_counter.services.template_service import TemplateService


def run() -> int:
    app = QApplication([])

    # --- core ---
    controller = GameController()

    # --- vision ---
    templates = TemplateService(Path(SPRITES_BG_DIR)).templates
    
    roi_templates = [
        (name, roi, templates[name])
        for name, roi in ROI_CONFIG
    ]
    
    detector = DetectionService(roi_templates)

    capture = CaptureService()

    # --- UI ---
    window = MainWindow()

    # --- WIRING (VERY IMPORTANT) ---

    capture.frame_ready.connect(detector.process_frame)
    detector.detection.connect(controller.on_detection)

    controller.pokemon_found.connect(window.sprite_strip.select_sprite)
    window.sprite_strip.count_changed.connect(window._update_counter)

    # --- start ---
    capture.start()
    window.show()

    return app.exec()
