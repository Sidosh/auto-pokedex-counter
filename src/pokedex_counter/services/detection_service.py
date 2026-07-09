# vision/detector.py
import cv2
from PySide6.QtCore import QObject, Signal

from pokedex_counter.config import FRAME_SIZE, THRESHOLD
from pokedex_counter.roi_config import SECTION_TRIGGERS


class DetectionService(QObject):
    detection = Signal(str)
    debug_scores = Signal(str, float)

    def __init__(self, roi_templates, threshold=THRESHOLD, debug=False):
        super().__init__()
        self.threshold = threshold
        self.debug = debug
        self._detected: set[str] = set()
        self._section_triggers = SECTION_TRIGGERS

        # roi -> [(name, resized_template, section_index), ...], grouped so
        # each distinct screen region is cropped/converted only once a frame.
        self._roi_groups: list[tuple[tuple[int, int, int, int], list[tuple[str, "cv2.Mat", int]]]] = []
        self.update_rois(roi_templates)

    def update_rois(self, roi_templates) -> None:
        """Rebuild the ROI/template grouping in place (e.g. after
        recalibration). Deliberately leaves `_detected` untouched - progress
        made so far in the current run must survive a recalibration."""
        group_by_roi = {}
        roi_groups = []
        for name, roi, template, section_index in roi_templates:
            resized = cv2.resize(template, (roi[2], roi[3]))
            group = group_by_roi.get(roi)
            if group is None:
                group = []
                group_by_roi[roi] = group
                roi_groups.append((roi, group))
            group.append((name, resized, section_index))
        self._roi_groups = roi_groups

    def _active_section(self) -> int:
        """The currently active section, derived live from `_detected` (not
        tracked incrementally) so undoing a trigger detection via forget()
        automatically rolls the active section back too - no separate
        mutable pointer to keep in sync."""
        last = len(self._section_triggers) - 1
        section = 0
        while section < last and self._section_triggers[section] in self._detected:
            section += 1
        return section

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, FRAME_SIZE)

        section = self._active_section()

        if self.debug:
            print(f"[section] active={section}")

        best_value = -1
        best_name = ""

        for roi, entries in self._roi_groups:
            active = [
                (name, template)
                for name, template, section_index in entries
                if section_index == section and name not in self._detected
            ]
            if not active:
                continue

            x, y, w, h = roi
            crop = frame[y:y + h, x:x + w]

            if crop.size == 0:
                continue

            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

            for name, template in active:
                result = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                if max_val > best_value:
                    best_value = max_val
                    best_name = name

        if self.debug and best_name:
            self.debug_scores.emit(best_name, best_value)

        if best_value > self.threshold and best_name not in self._detected:
            self._detected.add(best_name)
            self.detection.emit(best_name)
            print(f"Detected {best_name}: {best_value}")

    def forget(self, name: str) -> None:
        self._detected.discard(name)
