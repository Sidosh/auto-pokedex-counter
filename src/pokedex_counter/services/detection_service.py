# vision/detector.py
import time
import cv2
from PySide6.QtCore import QObject, Signal


class DetectionService(QObject):
    detection = Signal(str)

    def __init__(self, roi_templates, threshold=0.8, cooldown_time=2.0):
        super().__init__()
        self.threshold = threshold
        self.cooldown_time = cooldown_time
        self.cooldowns: dict[str, float] = {}

        # Resize each template to its own ROI's dimensions once, up front,
        # not per-frame.
        self._entries = [
            {
                "name": name,
                "roi": roi,
                "template": cv2.resize(template, (roi[2], roi[3])),
            }
            for name, roi, template in roi_templates
        ]

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (320, 180))

        for entry in self._entries:
            x, y, w, h = entry["roi"]
            crop = frame[y:y + h, x:x + w]

            if crop.size == 0:
                continue

            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(crop_gray, entry["template"], cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > self.threshold:
                name = entry["name"]
                now = time.time()

                if now - self.cooldowns.get(name, 0) > self.cooldown_time:
                    self.cooldowns[name] = now
                    self.detection.emit(name)
                    
    def clear_cooldown(self, name: str) -> None:
        self.cooldowns.pop(name, None)