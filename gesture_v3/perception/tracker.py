import mediapipe as mp
import os
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

try:
    from .. import config
except ImportError:
    import config

class HandTracker:
    """
    Detects hand landmarks using MediaPipe.
    Uses VIDEO mode for smooth temporal tracking.
    """
    def __init__(self, model_path="hand_landmarker.task"):
        self.model_path = model_path
        
        # Check if model exists, look in parent directory if needed
        if not os.path.exists(self.model_path):
            if os.path.exists("../" + model_path):
                self.model_path = "../" + model_path
            else:
                raise FileNotFoundError(f"Model not found: {model_path}")

        # Initialize MediaPipe hand landmarker
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        # Pre-initialize CLAHE once to avoid recreating per frame
        self.clahe = None
        if getattr(config, 'ENABLE_CLAHE_ENHANCER', False):
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def process(self, image_rgb, timestamp_ms):
        """
        Process frame and detect hand landmarks.
        - image_rgb: OpenCV image in RGB format
        - timestamp_ms: Frame timestamp in milliseconds (must be increasing)
        Returns: Detection result with hand landmarks
        """
        # Low-light contrast enhancement (only if enabled and room is actually dark)
        if self.clahe is not None and getattr(config, 'ENABLE_CLAHE_ENHANCER', False):
            try:
                # Fast brightness sample check
                if image_rgb.mean() < 60:
                    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
                    l, a, b = cv2.split(lab)
                    cl = self.clahe.apply(l)
                    limg = cv2.merge((cl, a, b))
                    image_rgb = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
            except Exception:
                pass

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.landmarker.detect_for_video(mp_image, int(timestamp_ms))
        return result
