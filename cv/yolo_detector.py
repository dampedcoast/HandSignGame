from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path='yolov8n.pt', confidence=0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < self.confidence:
                    continue

                cls = int(box.cls[0])
                label = self.model.names[cls]

                x1, y1, x2, y2 = box.xyxy[0]
                detections.append({
                    "label": label,
                    "conf": conf,
                    "bbox": (float(x1), float(y1), float(x2), float(y2))  # ✅ xyxy
                })

        return detections
