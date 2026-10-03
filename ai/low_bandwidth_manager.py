import cv2
import numpy as np

class CameraQualityAssessor:
    def __init__(self):
        """
        Evaluates camera quality parameters under rural/semi-urban deployment constraints:
        - Resolution adequacy
        - Lighting / Brightness
        - Blur / Sharpness (Laplacian variance)
        """
        pass

    def assess_quality(self, frame):
        """
        Returns:
            status (str): GOOD | FAIR | POOR
            metrics (dict): Resolution, brightness, blur_score
            reasons (list): Plain-text feedback on camera feed
        """
        if frame is None:
            return "POOR", {"resolution": "0x0", "brightness": 0, "blur": 0}, ["Camera feed unavailable or frame corrupted"]

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Blur evaluation using Laplacian variance
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 2. Brightness evaluation (mean pixel intensity)
        brightness = np.mean(gray)

        reasons = []

        # Resolution check
        res_ok = (w >= 640 and h >= 480)
        if not res_ok:
            reasons.append(f"Low resolution ({w}x{h}). Minimum 640x480 recommended.")

        # Brightness check
        if brightness < 40:
            reasons.append(f"Low lighting (Brightness: {brightness:.1f}/255). Night/dark classroom feed.")
        elif brightness > 220:
            reasons.append(f"Overexposed lighting (Brightness: {brightness:.1f}/255). High glare.")

        # Blur check
        if blur_score < 50.0:
            reasons.append(f"Image is blurry (Laplacian variance: {blur_score:.1f}). Camera lens dirty or out of focus.")

        # Categorize overall status
        if blur_score < 30.0 or brightness < 25 or not res_ok:
            status = "POOR"
        elif blur_score < 70.0 or brightness < 50 or brightness > 200:
            status = "FAIR"
        else:
            status = "GOOD"

        if not reasons:
            reasons.append("Camera feed parameters (Resolution, Brightness, Focus) optimal.")

        metrics = {
            "resolution": f"{w}x{h}",
            "brightness": round(float(brightness), 1),
            "blur_score": round(float(blur_score), 1)
        }

        return status, metrics, reasons

class LowBandwidthManager:
    def __init__(self, mode_enabled=True, sample_interval=3, target_resolution=(640, 360)):
        """
        Genuine Low Bandwidth Mode Manager for Rural/Semi-urban Deployment.
        - Frame downsampling & resizing
        - Skip non-key frames
        - Event-driven evidence transmission only
        """
        self.mode_enabled = mode_enabled
        self.sample_interval = sample_interval
        self.target_resolution = target_resolution
        self.frames_processed = 0
        self.frames_skipped = 0
        self.evidence_frames_generated = 0

    def process_frame_decision(self, frame, frame_index):
        """
        Decides whether to process or skip frame based on Low Bandwidth Mode.
        Returns:
            should_process (bool)
            processed_frame (np.ndarray)
        """
        if frame is None:
            return False, None

        if not self.mode_enabled:
            self.frames_processed += 1
            return True, frame

        # In Low Bandwidth Mode, sample 1 out of every `sample_interval` frames
        if frame_index % self.sample_interval != 0:
            self.frames_skipped += 1
            return False, None

        self.frames_processed += 1
        
        # Downsample resolution to conserve processing & transmission bandwidth
        h, w = frame.shape[:2]
        if w > self.target_resolution[0]:
            resized = cv2.resize(frame, self.target_resolution, interpolation=cv2.INTER_AREA)
        else:
            resized = frame.copy()

        return True, resized

    def get_bandwidth_stats(self):
        """
        Calculates estimated bandwidth and compute savings.
        """
        total = self.frames_processed + self.frames_skipped
        skip_pct = (self.frames_skipped / total * 100) if total > 0 else 0.0
        
        # Estimated data reduction (Architecture-level estimate)
        est_data_saved_mb = round((self.frames_skipped * 0.15), 2) # ~150KB per frame saving

        return {
            "mode_enabled": self.mode_enabled,
            "frames_processed": self.frames_processed,
            "frames_skipped": self.frames_skipped,
            "skip_percentage": round(skip_pct, 1),
            "est_data_saved_mb": est_data_saved_mb,
            "evidence_frames_generated": self.evidence_frames_generated
        }

if __name__ == "__main__":
    assessor = CameraQualityAssessor()
    sample = np.ones((480, 640, 3), dtype=np.uint8) * 120
    status, metrics, reasons = assessor.assess_quality(sample)
    print(f"Camera Quality Test: Status={status}, Metrics={metrics}")

    lbm = LowBandwidthManager(mode_enabled=True)
    for i in range(10):
        proc, _ = lbm.process_frame_decision(sample, i)
        print(f"Frame {i}: Processed={proc}")
    print("Bandwidth Stats:", lbm.get_bandwidth_stats())
