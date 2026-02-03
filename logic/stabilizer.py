import time

class Stabilizer:
    def __init__(self, window_ms=200):
        self.window_s = window_ms / 1000.0
        self.current_sign = None
        self.last_sign = None
        self.start_time = 0

    def update(self, detected_sign):
        if detected_sign is None:
            self.current_sign = None
            self.last_sign = None
            self.start_time = 0
            return None

        if detected_sign == self.last_sign:
            if time.time() - self.start_time >= self.window_s:
                if self.current_sign != detected_sign:
                    self.current_sign = detected_sign
                    return self.current_sign
        else:
            self.last_sign = detected_sign
            self.start_time = time.time()
        
        return None # No change or not stabilized yet
