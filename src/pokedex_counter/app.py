from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QSettings

from pokedex_counter.calibration_runner import run_calibration
from pokedex_counter.camera import resolve_camera_index
from pokedex_counter.config import APP_NAME, ORGANIZATION_NAME, SPRITES_BG_DIR
from pokedex_counter.controllers.game_controller import GameController
from pokedex_counter.main_window import MainWindow
from pokedex_counter.services.capture_service import CaptureService
from pokedex_counter.services.detection_service import DetectionService
from pokedex_counter.services.pb_service import save_pb
from pokedex_counter.services.template_service import TemplateService
from pokedex_counter.services.wr_service import load_wr_sections
from pokedex_counter.settings_window import SettingsWindow


def run() -> int:
    camera_index = resolve_camera_index()

    from pokedex_counter.roi_config import build_detection_entries

    app = QApplication([])

    # --- core ---
    controller = GameController()

    # --- vision ---
    templates = TemplateService(Path(SPRITES_BG_DIR)).templates
    roi_templates = build_detection_entries(templates)  # defaults; no boot-time calibration

    detector = DetectionService(roi_templates)

    capture = CaptureService(camera_index=camera_index)

    # --- UI ---
    window = MainWindow()
    settings = SettingsWindow()
    window.set_calibrated(bool(roi_templates))

    # --- persisted settings ---
    prefs = QSettings(ORGANIZATION_NAME, APP_NAME)
    settings.columns_spinbox.setValue(int(prefs.value("sprites_per_row", settings.columns_spinbox.value())))
    settings.font_size_spinbox.setValue(int(prefs.value("counter_font_size", settings.font_size_spinbox.value())))
    settings.compare_to_wr_checkbox.setChecked(prefs.value("compare_to_wr", settings.compare_to_wr_checkbox.isChecked(), type=bool))
    settings.columns_spinbox.valueChanged.connect(lambda v: prefs.setValue("sprites_per_row", v))
    settings.font_size_spinbox.valueChanged.connect(lambda v: prefs.setValue("counter_font_size", v))
    settings.compare_to_wr_checkbox.toggled.connect(lambda checked: prefs.setValue("compare_to_wr", checked))

    # --- WR (world record) comparison ---
    wr_sections = load_wr_sections()

    def apply_wr_section(section_index: int) -> None:
        if settings.compare_to_wr_checkbox.isChecked():
            window.sprite_strip.mark_wr_section(wr_sections.get(section_index, set()))

    def apply_wr_up_to_current() -> None:
        """Backfill every section's marks up to the active one - not just
        the current one - so re-enabling mid-run (or starting up already
        past section 0) still flags every WR pokemon missed so far, not
        only ones from here on."""
        for section_index in range(detector.current_section() + 1):
            apply_wr_section(section_index)

    def on_compare_to_wr_toggled(checked: bool) -> None:
        if checked:
            apply_wr_up_to_current()
        else:
            window.sprite_strip.clear_wr_marks()

    detector.section_changed.connect(apply_wr_section)
    settings.compare_to_wr_checkbox.toggled.connect(on_compare_to_wr_toggled)

    # --- WIRING (VERY IMPORTANT) ---

    capture.frame_ready.connect(detector.process_frame, Qt.ConnectionType.DirectConnection)
    detector.detection.connect(controller.on_detection)
    detector.section_changed.connect(controller.on_section_changed)

    controller.pokemon_found.connect(window.sprite_strip.select_sprite)
    window.sprite_strip.sprite_deselected.connect(controller.forget)
    window.sprite_strip.sprite_deselected.connect(detector.forget)
    window.sprite_strip.count_changed.connect(window._update_counter)

    settings.columns_spinbox.valueChanged.connect(window.set_sprites_per_row)
    settings.font_size_spinbox.valueChanged.connect(window.set_counter_font_size)

    def maybe_prompt_save_pb() -> None:
        """If the current run has the full 151, ask whether to save it as
        PB.json before its progress is lost (reset or app close)."""
        if window.sprite_strip.caught_count() != 151:
            return

        reply = QMessageBox.question(
            window,
            "Save Personal Best?",
            "You've caught all 151 Pokémon! Save this run as your PB?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            save_pb(controller.section_catches)

    def on_reset_clicked() -> None:
        maybe_prompt_save_pb()
        window.sprite_strip.reset()

    settings.reset_button.clicked.connect(on_reset_clicked)
    app.aboutToQuit.connect(maybe_prompt_save_pb)

    def on_calibrate_clicked() -> None:
        nonlocal capture
        capture.stop()
        locked = run_calibration(camera_index=camera_index)
        if locked:
            new_roi_templates = build_detection_entries(templates, locked)
            detector.update_rois(new_roi_templates)
            window.set_calibrated(bool(new_roi_templates))
        capture = CaptureService(camera_index=camera_index)
        capture.frame_ready.connect(detector.process_frame, Qt.ConnectionType.DirectConnection)
        capture.start()

    settings.calibrate_button.clicked.connect(on_calibrate_clicked)

    # --- start ---
    window.set_sprites_per_row(settings.columns_spinbox.value())
    window.set_counter_font_size(settings.font_size_spinbox.value())
    if settings.compare_to_wr_checkbox.isChecked():
        apply_wr_up_to_current()
    capture.start()
    window.show()
    settings.move(window.x() + window.frameGeometry().width() + 10, window.y())
    settings.show()

    return app.exec()
