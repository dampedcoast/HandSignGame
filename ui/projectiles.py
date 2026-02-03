# ui/projectiles.py
import time

class GifProjectile:
    """
    Moves from start_pos -> end_pos over 'travel_time' seconds.
    Uses a GifVFX instance to animate the fireball frames.
    """
    def __init__(self, gif_vfx, start_pos, end_pos, travel_time=0.6, size_px=220):
        self.vfx = gif_vfx
        self.start = start_pos
        self.end = end_pos
        self.travel_time = max(0.05, float(travel_time))
        self.size_px = int(size_px)

        self.t0 = time.time()
        self.done = False
        self.pos = start_pos

    def update(self):
        if self.done:
            return None

        # advance animation frame
        frame = self.vfx.update()
        # even if GIF ends early, we can still keep last frame; but simplest: stop if None
        if frame is None:
            self.done = True
            return None

        # update position by time
        t = (time.time() - self.t0) / self.travel_time
        if t >= 1.0:
            t = 1.0
            self.done = True

        x = int(self.start[0] + (self.end[0] - self.start[0]) * t)
        y = int(self.start[1] + (self.end[1] - self.start[1]) * t)
        self.pos = (x, y)

        return frame

    def release(self):
        self.vfx.release()
