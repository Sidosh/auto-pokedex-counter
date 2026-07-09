import cv2
from PySide6.QtCore import QThread, Signal

class CaptureService(QThread):
    frame_ready = Signal(object)

    def __init__(self, camera_index=2):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.running = True

    def run(self):
        if not self.cap.isOpened():
            print(f"[CaptureService] ERROR: could not open camera index {self.camera_index}")
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.frame_ready.emit(frame)

    def stop(self):
        self.running = False
        self.cap.release()
        self.wait()
