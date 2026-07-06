import time

import cv2
import numpy as np

from pokedex_counter.config import FRAME_SIZE
from pokedex_counter.vision.template_matching import find_best_match

DEFAULT_SCALES = np.linspace(0.1, 5.0, 500)
DEFAULT_LOCK_THRESHOLD = 0.85

class CalibrationService:
    def __init__(self, camera_index=2, lock_threshold=DEFAULT_LOCK_THRESHOLD, scales=DEFAULT_SCALES):
        self.camera_index = camera_index
        self.lock_threshold = lock_threshold
        self.scales = scales

    def run(self, templates: dict[str, np.ndarray], timeout: float | None = None) -> dict[str, tuple[int, int, int, int]]:
        pending = dict(templates)
        locked: dict[str, tuple[int, int, int, int]] = {}

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open camera index {self.camera_index}")

        start = time.time()
        print(f"[Calibration] Waiting for: {', '.join(pending)}")
        print("ESC to abort.\n")

        try:
            while pending:
                if timeout is not None and time.time() - start > timeout:
                    print(f"[Calibration] Timed out with {list(pending)} unlocked.")
                    break

                ret, frame = cap.read()
                if not ret:
                    continue

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, FRAME_SIZE)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                display = frame.copy()
                newly_locked = []

                for name, template in pending.items():
                    best_val, best_box = find_best_match(frame_gray, template, self.scales)

                    if best_box is not None:
                        x, y, w, h = best_box
                        confident = best_val >= self.lock_threshold
                        color = (0, 255, 0) if confident else (0, 165, 255)
                        cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(display, f"{name}: {best_val:.2f}", (x, max(y - 8, 12)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        if confident:
                            locked[name] = best_box
                            newly_locked.append(name)
                            print(f"[Calibration] Locked {name} = {best_box}  (score={best_val:.3f})")

                for name in newly_locked:
                    pending.pop(name)

                cv2.imshow("Calibration", display)

                if cv2.waitKey(1) & 0xFF == 27:
                    print("[Calibration] Aborted by user.")
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        return locked