# vision/detector.py
import cv2
import time
from PySide6.QtCore import QObject, Signal

from pokedex_counter.config import THRESHOLD

class DetectionService(QObject):
    detection = Signal(str)

    def __init__(self, templates, rois):
        super().__init__()
        self.templates = templates
        self.rois = rois
        self.cooldowns = {}
        self.cooldown_time = 2.0

        self._resized_cache: dict[int, tuple[tuple[int, int], dict]] = {}

    def _get_resized_templates(self, roi_index: int, shape: tuple[int, int]) -> dict:
        cached = self._resized_cache.get(roi_index)
        if cached is not None and cached[0] == shape:
            return cached[1]

        h, w = shape
        resized = {
            name: cv2.resize(template, (w, h))
            for name, template in self.templates.items()
        }
        self._resized_cache[roi_index] = (shape, resized)
        return resized

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))

        for roi_index, (x, y, w, h) in enumerate(self.rois):
            roi = frame[y:y + h, x:x + w]
            if roi.size == 0:
                continue

            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            resized_templates = self._get_resized_templates(roi_index, roi_gray.shape[:2])

            best_name = None
            best_score = 0.0

            for name, template in resized_templates.items():
                result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                if max_val > best_score:
                    best_score = max_val
                    best_name = name

                    if best_score > 0.90:
                        break  # near-perfect match, stop scanning this ROI early

            if best_name is not None and best_score > THRESHOLD:
                now = time.time()
                if now - self.cooldowns.get(best_name, 0) > self.cooldown_time:
                    self.cooldowns[best_name] = now
                    self.detection.emit(best_name)