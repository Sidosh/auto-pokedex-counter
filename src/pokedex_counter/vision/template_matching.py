import cv2
import numpy as np

def find_best_match(frame_gray: np.ndarray, template: np.ndarray, scales: np.ndarray):
    best_val = -1.0
    best_box = None

    th, tw = template.shape[:2]
    fh, fw = frame_gray.shape[:2]

    for scale in scales:
        w = int(tw * scale)
        h = int(th * scale)

        if w < 8 or h < 8 or w > fw or h > fh:
            continue

        resized = cv2.resize(template, (w, h))
        result = cv2.matchTemplate(frame_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_val:
            best_val = max_val
            best_box = (max_loc[0], max_loc[1], w, h)

    return best_val, best_box