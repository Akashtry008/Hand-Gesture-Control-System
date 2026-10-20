import cv2
import numpy as np

try:
    import pyvirtualcam
except ImportError:
    pyvirtualcam = None

class VirtualCamStreamer:
    """
    Streams the mirrored webcam feed with holographic HUD overlays into a Virtual Camera
    device, allowing Zoom, Google Meet, Teams, Discord, and OBS to use Project Air.
    """
    def __init__(self, width=1280, height=720, fps=60):
        self.width = width
        self.height = height
        self.fps = fps
        self.cam = None
        self.is_active = False
        self.is_available = False
        self.error_msg = ""
        
        self._check_availability()

    def _check_availability(self):
        if pyvirtualcam is None:
            self.error_msg = "pyvirtualcam not installed"
            return
        self.is_available = True

    def toggle(self):
        """Toggle virtual camera streaming on/off"""
        if self.is_active:
            self.stop()
            return False, "Virtual Camera Stopped"
        else:
            success, msg = self.start()
            return success, msg

    def start(self):
        """Initialize the virtual camera device"""
        if not self.is_available:
            return False, "pyvirtualcam library not found"

        if self.is_active and self.cam is not None:
            return True, "Virtual Camera already active"

        try:
            # Format: BGR for OpenCV compatibility
            self.cam = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.BGR,
                print_fps=False
            )
            self.is_active = True
            device_name = getattr(self.cam, "device", "Virtual Camera")
            print(f"[VirtualCam] Streaming to: {device_name}")
            return True, f"Streaming to {device_name}"
        except Exception as e:
            self.is_active = False
            self.cam = None
            self.error_msg = str(e)
            print(f"[VirtualCam] Could not start virtual camera: {e}")
            return False, "No Virtual Cam Driver (Start OBS Virtual Cam first)"

    def send(self, frame_bgr):
        """Send current OpenCV frame to virtual camera"""
        if not self.is_active or self.cam is None:
            return
        try:
            # Ensure frame matches exact width/height
            if frame_bgr.shape[1] != self.width or frame_bgr.shape[0] != self.height:
                frame_bgr = cv2.resize(frame_bgr, (self.width, self.height))
            self.cam.send(frame_bgr)
            self.cam.sleep_until_next_frame()
        except Exception as e:
            print(f"[VirtualCam] Send error: {e}")
            self.stop()

    def stop(self):
        """Release virtual camera device"""
        if self.cam is not None:
            try:
                self.cam.close()
            except Exception:
                pass
            self.cam = None
        self.is_active = False
        print("[VirtualCam] Stopped")
