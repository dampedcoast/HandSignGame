import cv2

class Camera:
    def __init__(self, camera_id=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.width = width
        self.height = height

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        return frame

    def release(self):
        self.cap.release()
