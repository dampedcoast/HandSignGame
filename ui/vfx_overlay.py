# ui/vfx_overlay.py
import cv2
import numpy as np

def overlay_png_at_point(base_bgr, png_bgra, center_xy, size_px=240, alpha=1.0):
    if png_bgra is None:
        return base_bgr

    H, W = base_bgr.shape[:2]
    cx, cy = center_xy

    png = cv2.resize(png_bgra, (size_px, size_px), interpolation=cv2.INTER_LINEAR)

    x1 = int(cx - size_px // 2)
    y1 = int(cy - size_px // 2)
    x2 = x1 + size_px
    y2 = y1 + size_px

    sx1, sy1 = max(0, x1), max(0, y1)
    sx2, sy2 = min(W, x2), min(H, y2)
    if sx2 <= sx1 or sy2 <= sy1:
        return base_bgr

    ex1, ey1 = sx1 - x1, sy1 - y1
    ex2, ey2 = ex1 + (sx2 - sx1), ey1 + (sy2 - sy1)

    region = base_bgr[sy1:sy2, sx1:sx2].astype(np.float32)
    eff = png[ey1:ey2, ex1:ex2].astype(np.float32)  # BGRA

    bgr = eff[:, :, :3]
    a = (eff[:, :, 3:4] / 255.0) * float(alpha)

    comp = region * (1.0 - a) + bgr * a
    base_bgr[sy1:sy2, sx1:sx2] = np.clip(comp, 0, 255).astype(np.uint8)
    return base_bgr


def overlay_gif_blackkey_at_point(base_bgr, gif_bgr, center_xy, size_px=240, black_thresh=35, alpha=1.0):
    """
    Overlay a GIF frame (BGR) that has a black background.
    Removes black pixels using a brightness threshold.
    """
    if gif_bgr is None:
        return base_bgr

    H, W = base_bgr.shape[:2]
    cx, cy = center_xy

    eff = cv2.resize(gif_bgr, (size_px, size_px), interpolation=cv2.INTER_LINEAR)

    x1 = int(cx - size_px // 2)
    y1 = int(cy - size_px // 2)
    x2 = x1 + size_px
    y2 = y1 + size_px

    sx1, sy1 = max(0, x1), max(0, y1)
    sx2, sy2 = min(W, x2), min(H, y2)
    if sx2 <= sx1 or sy2 <= sy1:
        return base_bgr

    ex1, ey1 = sx1 - x1, sy1 - y1
    ex2, ey2 = ex1 + (sx2 - sx1), ey1 + (sy2 - sy1)

    region = base_bgr[sy1:sy2, sx1:sx2].astype(np.float32)
    e = eff[ey1:ey2, ex1:ex2].astype(np.float32)

    brightness = np.max(e, axis=2)  # 0..255
    mask = (brightness > float(black_thresh)).astype(np.float32)[..., None]

    a = float(alpha)
    comp = region * (1.0 - mask * a) + e * (mask * a)
    base_bgr[sy1:sy2, sx1:sx2] = np.clip(comp, 0, 255).astype(np.uint8)
    return base_bgr
import cv2
import numpy as np

def overlay_gif_greenscreen_at_point(base_bgr, gif_bgr, center_xy, size_px=320,
                                    key_green=(0, 255, 0), tol=80, alpha=1.0):
    """
    Overlay a GIF frame (BGR) that has a green-screen background.
    Removes pixels close to key_green.
    tol: bigger = removes more green.
    """
    if gif_bgr is None:
        return base_bgr

    H, W = base_bgr.shape[:2]
    cx, cy = center_xy

    eff = cv2.resize(gif_bgr, (size_px, size_px), interpolation=cv2.INTER_LINEAR)

    x1 = int(cx - size_px // 2)
    y1 = int(cy - size_px // 2)
    x2 = x1 + size_px
    y2 = y1 + size_px

    sx1, sy1 = max(0, x1), max(0, y1)
    sx2, sy2 = min(W, x2), min(H, y2)
    if sx2 <= sx1 or sy2 <= sy1:
        return base_bgr

    ex1, ey1 = sx1 - x1, sy1 - y1
    ex2, ey2 = ex1 + (sx2 - sx1), ey1 + (sy2 - sy1)

    region = base_bgr[sy1:sy2, sx1:sx2].astype(np.float32)
    e = eff[ey1:ey2, ex1:ex2].astype(np.float32)

    key = np.array(key_green, dtype=np.float32).reshape(1, 1, 3)
    dist = np.linalg.norm(e - key, axis=2)  # distance from green
    mask = (dist > float(tol)).astype(np.float32)[..., None]  # keep non-green

    a = float(alpha)
    comp = region * (1.0 - mask * a) + e * (mask * a)
    base_bgr[sy1:sy2, sx1:sx2] = np.clip(comp, 0, 255).astype(np.uint8)
    return base_bgr
