# ui/vfx_gif.py
import time
import cv2
import numpy as np
from PIL import Image, ImageSequence

class GifVFX:
    def __init__(self, path, loop=False, fps=30):
        self.path = path
        self.loop = loop
        self.fps = fps
        self.frame_dt = 1.0 / float(fps)

        self.frames = []
        self._load_frames()

        if not self.frames:
            raise RuntimeError(f"Could not load GIF frames: {path}")

        self.i = 0
        self.last_t = time.time()
        self.done = False

    def _load_frames(self):
        img = Image.open(self.path)
        for frame in ImageSequence.Iterator(img):
            # Convert to RGBA, then to BGR for OpenCV pipeline
            rgba = frame.convert("RGBA")
            arr = np.array(rgba)  # (H,W,4) RGBA
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            self.frames.append(bgr)

    def update(self):
        if self.done:
            return None

        now = time.time()
        if (now - self.last_t) >= self.frame_dt:
            self.i += 1
            self.last_t = now

            if self.i >= len(self.frames):
                if self.loop:
                    self.i = 0
                else:
                    self.done = True
                    return None

        return self.frames[self.i]

    def release(self):
        pass
