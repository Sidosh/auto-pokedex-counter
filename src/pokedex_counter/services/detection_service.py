# vision/detector.py
from pathlib import Path
import time
import cv2
from PySide6.QtCore import QObject, Signal

from pokedex_counter.config import FRAME_SIZE, THRESHOLD


class DetectionService(QObject):
    detection = Signal(str)
    debug_scores = Signal(str, float)

    def __init__(self, roi_templates, threshold=THRESHOLD, cooldown_time=2.0, debug=False):
        super().__init__()
        self.threshold = threshold
        self.cooldown_time = cooldown_time
        self.cooldowns: dict[str, float] = {}
        self.debug = debug

        self._roi_groups: list[tuple[tuple[int, int, int, int], list[tuple[str, "cv2.Mat"]]]] = []
        group_by_roi = {}
        for name, roi, template in roi_templates:
            resized = cv2.resize(template, (roi[2], roi[3]))
            group = group_by_roi.get(roi)
            if group is None:
                group = []
                group_by_roi[roi] = group
                self._roi_groups.append((roi, group))
            group.append((name, resized))

        self.timestamp = time.strftime("%Y%m%d_%H%M%S")

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, FRAME_SIZE)

        best_value = -1
        best_name = ""

        for roi, entries in self._roi_groups:
            x, y, w, h = roi
            crop = frame[y:y + h, x:x + w]

            if crop.size == 0:
                continue

            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

            for name, template in entries:
                result = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                if max_val > best_value:
                    best_value = max_val
                    best_name = name

        if self.debug and best_name:
            self.debug_scores.emit(best_name, best_value)

        if best_value > self.threshold:
            now = time.time()

            if now - self.cooldowns.get(best_name, 0) > self.cooldown_time:
                self.cooldowns[best_name] = now
                self.detection.emit(best_name)
                print(f"Detected {best_name}: {best_value}")
                screenshot_path = Path(f"screenshots_{self.timestamp}/{best_name}.png")
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(screenshot_path), frame)

    def clear_cooldown(self, name: str) -> None:
        self.cooldowns.pop(name, None)
