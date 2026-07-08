import cv2
import numpy as np

_COARSE_SAMPLES = 40


def find_best_match(frame_gray: np.ndarray, template: np.ndarray, scales: np.ndarray):
    scales = np.asarray(scales)
    n = len(scales)
    if n == 0:
        return -1.0, None

    th, tw = template.shape[:2]
    fh, fw = frame_gray.shape[:2]

    def score_at(idx):
        scale = scales[idx]
        w = int(tw * scale)
        h = int(th * scale)

        if w < 8 or h < 8 or w > fw or h > fh:
            return None

        resized = cv2.resize(template, (w, h))
        result = cv2.matchTemplate(frame_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val, (max_loc[0], max_loc[1], w, h)

    step = max(1, n // _COARSE_SAMPLES)
    coarse_indices = list(range(0, n, step))
    if coarse_indices[-1] != n - 1:
        coarse_indices.append(n - 1)

    best_val = -1.0
    best_box = None
    best_idx = None

    for idx in coarse_indices:
        scored = score_at(idx)
        if scored is None:
            continue
        val, box = scored
        if val > best_val:
            best_val, best_box, best_idx = val, box, idx

    if best_idx is None:
        return best_val, best_box

    coarse_set = set(coarse_indices)
    lo = max(0, best_idx - step)
    hi = min(n - 1, best_idx + step)

    for idx in range(lo, hi + 1):
        if idx in coarse_set:
            continue
        scored = score_at(idx)
        if scored is None:
            continue
        val, box = scored
        if val > best_val:
            best_val, best_box = val, box

    return best_val, best_box
