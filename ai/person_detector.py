import cv2
import time
import numpy as np
import torch
from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_weight='yolov8n.pt', conf_thresh=0.45):
        """
        Privacy-Preserving Person Detector using YOLOv8/YOLO11.
        Strictly filters for class 0 (person). No face recognition or individual ID tracking.
        """
        self.conf_thresh = conf_thresh
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[PersonDetector] Initializing YOLO Person Detector using device: {self.device}")
        try:
            self.model = YOLO(model_weight)
        except Exception as e:
            print(f"[PersonDetector] Error loading weights {model_weight}, falling back to yolov8n.pt: {e}")
            self.model = YOLO('yolov8n.pt')

    def detect(self, image_input):
        """
        Processes an OpenCV image BGR array or filepath.
        Returns:
            annotated_img (np.ndarray): Image with bounding box annotations
            person_count (int): Number of detected persons
            avg_confidence (float): Mean confidence score (0-100%)
            detections (list): List of dicts with box coordinates and confidence
        """
        if isinstance(image_input, str):
            frame = cv2.imread(image_input)
            if frame is None:
                raise ValueError(f"Could not read image file at {image_input}")
        else:
            frame = image_input.copy()

        start_time = time.time()
        # Class 0 is 'person' in standard COCO dataset
        results = self.model(frame, classes=[0], conf=self.conf_thresh, device=self.device, verbose=False)[0]
        fps = 1.0 / (time.time() - start_time + 1e-6)

        person_count = 0
        conf_scores = []
        detections = []

        annotated_frame = frame.copy()

        for box in results.boxes:
            person_count += 1
            conf = float(box.conf[0].cpu().numpy())
            conf_scores.append(conf)
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy

            detections.append({
                "box": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": round(conf * 100, 1)
            })

            # Draw bounding box (Privacy-preserving box only)
            color = (0, 215, 255) # Sleek amber/gold box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Label box
            label = f"Trainee {person_count} ({conf*100:.1f}%)"
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(annotated_frame, (x1, y1 - t_size[1] - 6), (x1 + t_size[0] + 4, y1), color, -1)
            cv2.putText(annotated_frame, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        avg_conf = (sum(conf_scores) / len(conf_scores) * 100) if conf_scores else 0.0

        # Header banner on image
        banner_text = f"AI Trainee Count: {person_count} | Confidence: {avg_conf:.1f}% | FPS: {fps:.1f}"
        cv2.putText(annotated_frame, banner_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        return annotated_frame, person_count, round(avg_conf, 1), detections, round(fps, 1)

if __name__ == "__main__":
    detector = PersonDetector()
    sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
    img, cnt, conf, dets, fps = detector.detect(sample_img)
    print(f"Test Successful: Count={cnt}, Conf={conf}%, FPS={fps}")
