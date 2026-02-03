import time

class InputBuffer:
    def __init__(self, max_length=5, time_window=1.5):
        self.max_length = max_length
        self.time_window = time_window
        self.buffer = [] # List of (sign, timestamp)

    def add_sign(self, sign):
        if sign is None:
            return
        
        now = time.time()
        self.buffer.append((sign, now))
        self._cleanup()
        
        if len(self.buffer) > self.max_length:
            self.buffer.pop(0)

    def _cleanup(self):
        now = time.time()
        self.buffer = [item for item in self.buffer if now - item[1] <= self.time_window]

    def get_sequence(self):
        self._cleanup()
        return [item[0] for item in self.buffer]

    def clear(self):
        self.buffer = []
