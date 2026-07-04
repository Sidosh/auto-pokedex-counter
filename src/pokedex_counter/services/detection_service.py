# vision/detector.py
import cv2
import time
from PySide6.QtCore import QObject, Signal

class DetectionService(QObject):
    detection = Signal(str)
    ROI = (348, 43, 100, 100)

    def __init__(self, templates):
        super().__init__()
        self.templates = templates
        self.cooldowns = {}
        self.cooldown_time = 2.0

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))

        # crop ROI
        x, y, w, h = self.ROI
        roi = frame[y:y+h, x:x+w]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        for name, template in self.templates.items():
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > 0.85:
                now = time.time()
                print("TEST")

                if now - self.cooldowns.get(name, 0) > self.cooldown_time:
                    self.cooldowns[name] = now
                    self.detection.emit(name)