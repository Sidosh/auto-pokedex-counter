# vision/detector.py
import cv2
import time
from PySide6.QtCore import QObject, Signal

from pokedex_counter.config import ROI, THRESHOLD

class DetectionService(QObject):
    detection = Signal(str)

    def __init__(self, templates):
        super().__init__()
        self.templates = templates
        self.cooldowns = {}
        self.cooldown_time = 2.0

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))

        x, y, w, h = ROI
        roi = frame[y:y+h, x:x+w]

        if roi.size == 0:
            return
        
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        best_name = None
        best_score = 0
    
        for name, template in self.templates.items():
            template_resized = cv2.resize(template, (roi_gray.shape[1], roi_gray.shape[0]))
            result = cv2.matchTemplate(roi_gray, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_name = name

        if best_score > THRESHOLD:
            now = time.time()
            print("DETECTED:", best_name, best_score)

            if now - self.cooldowns.get(best_name, 0) > self.cooldown_time:
                self.cooldowns[best_name] = now
                self.detection.emit(best_name)