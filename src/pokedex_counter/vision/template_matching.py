import cv2
import numpy as np

from pokedex_counter.config import MIN_SHADE_SEPARATION

_COARSE_SAMPLES = 40
_KMEANS_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)


def canonicalize_shades(gray: np.ndarray, k: int = 4, min_separation: float = MIN_SHADE_SEPARATION) -> np.ndarray | None:
    """Remap `gray` to one of `k` fixed evenly-spaced levels (0/85/170/255
    for k=4) by each pixel's cluster's brightness *rank*, not its absolute
    value. A Game Boy screen always has k=4 underlying shade classes, but
    each of the GBC's 13 hardware color palettes assigns different actual
    luminance to each - rank-based remapping makes two renders of the same
    underlying shade pattern produce an identical result regardless of the
    palette, as long as it preserves relative shade ordering (all of them
    do except "Negative", which reverses it). Since this only preserves
    *order* and discards absolute brightness, canonicalizing an inverted
    render produces the exact bitwise complement of the non-inverted
    result - callers recover Negative-style palettes by additionally
    matching against `255 - canonicalize_shades(...)`, with no need to
    know which palette is actually active.

    Returns None if the clustering isn't trustworthy - e.g. a blank or
    in-transition crop with no real 4-shade content would otherwise have
    its noise rank-remapped into a fabricated full-contrast pattern.
    """
    samples = gray.reshape(-1, 1).astype(np.float32)
    _, labels, centers = cv2.kmeans(samples, k, None, _KMEANS_CRITERIA, 3, cv2.KMEANS_PP_CENTERS)

    centers = centers.flatten()
    order = np.argsort(centers)
    if np.diff(centers[order]).min() < min_separation:
        return None

    rank_of_cluster = np.empty(k, dtype=np.int64)
    rank_of_cluster[order] = np.arange(k)
    canonical_levels = np.linspace(0, 255, k).astype(np.uint8)

    remapped = canonical_levels[rank_of_cluster[labels.flatten()]]
    return remapped.reshape(gray.shape)


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
