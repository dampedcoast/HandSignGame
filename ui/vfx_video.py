import cv2
import time

class VideoVFX:
    def __init__(self, path, loop=False, fps_override=None):
        self.path = path
        self.loop = loop
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open VFX video: {path}")

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps_override or (fps if fps and fps > 1 else 30.0)
        self.frame_dt = 1.0 / float(self.fps)

        self.last_t = 0.0
        self.frame = None
        self.done = False
        self.restart()

    def restart(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.last_t = time.time()
        self.done = False
        self.frame = None

    def update(self):
        if self.done:
            return None

        now = time.time()
        if self.frame is None or (now - self.last_t) >= self.frame_dt:
            ok, frame = self.cap.read()
            if not ok:
                if self.loop:
                    self.restart()
                    ok, frame = self.cap.read()
                    if not ok:
                        self.done = True
                        return None
                else:
                    self.done = True
                    return None
            self.frame = frame
            self.last_t = now

        return self.frame

    def release(self):
        self.cap.release()
