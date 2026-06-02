
import cv2
import numpy as np
from collections import deque
from gesture_v3 import config

class CinematicHUD:
    """
    Renders heads-up display with hand tracking visualization and state indicators.
    """
    def __init__(self):
        self.trail = deque(maxlen=20)  # Hand movement trail history
        self.pulse_phase = 0.0  # Animation phase

    def draw(self, img, hand_landmarks, state, confidence):
        """
        Draw HUD overlay on camera frame.
        - img: Video frame (BGR)
        - hand_landmarks: MediaPipe hand landmark data
        - state: Current gesture state
        - confidence: Gesture confidence score (0-1)
        """
        if not hand_landmarks:
            self.trail.clear()
            return
            
        h, w, _ = img.shape
        
        # Calculate hand center position
        hand_center = self._get_hand_center(hand_landmarks, w, h)
        cx, cy = hand_center
        
        # Update and draw trail
        self.trail.appendleft((cx, cy))
        self._draw_trail(img)
        
        # Update animation
        self.pulse_phase += 0.1
        
        # Draw state-specific indicators
        self._draw_state_indicator(img, state, cx, cy)
        
        # Draw status text
        cv2.putText(img, f"STATUS: {state}", (cx + 50, cy - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _get_hand_center(self, landmarks, w, h):
        """Calculate hand center from palm landmarks"""
        idx_base = landmarks[5]  # Index MCP
        pinky_base = landmarks[17]  # Pinky MCP
        wrist = landmarks[0]
        
        cx = int((idx_base.x + pinky_base.x + wrist.x) / 3 * w)
        cy = int((idx_base.y + pinky_base.y + wrist.y) / 3 * h)
        return cx, cy
    
    def _draw_trail(self, img):
        """Draw hand movement trail"""
        for i in range(1, len(self.trail)):
            thickness = int(np.sqrt(20 / i) * 2)
            cv2.line(img, self.trail[i-1], self.trail[i], config.COLOR_IDLE, thickness)
    
    def _draw_state_indicator(self, img, state, cx, cy):
        """Draw state-specific visual indicator"""
        radius = int(40 + np.sin(self.pulse_phase) * 5)
        color = config.COLOR_IDLE
        
        if state == "MOVE":
            color = config.COLOR_MOVE
            radius = 20
        elif state == "FAST_MOVE":
            color = (0, 255, 255)
            radius = 22
            cv2.putText(img, "FAST", (cx + 50, cy - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        elif state == "CLICK_LEFT":
            color = config.COLOR_CLICK
            radius = 35
            cv2.circle(img, (cx, cy), radius, color, 3)
        elif state == "CLICK_RIGHT":
            color = config.COLOR_RIGHT_CLICK
            radius = 35
            cv2.putText(img, "R", (cx - 10, cy + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        elif state == "DRAG_ACTIVE":
            color = config.COLOR_DRAG_ACTIVE
            radius = 35
            cv2.circle(img, (cx, cy), radius, color, 4)
            cv2.rectangle(img, (cx - 10, cy - 10), (cx + 10, cy + 10), color, -1)
        elif state == "FIST":
            color = (0, 165, 255)  # Orange
            radius = 30
            cv2.putText(img, "TOGGLE", (cx - 25, cy - 40), 
                       cv2.FONT_HERSHEY_PLAIN, 1, color, 1)
        elif state == "SCROLL":
            color = config.COLOR_SCROLL
            radius = 45
            cv2.arrowedLine(img, (cx, cy - 20), (cx, cy - 60), color, 2)
            cv2.arrowedLine(img, (cx, cy + 20), (cx, cy + 60), color, 2)

        # Draw animated reticle
        cv2.ellipse(img, (cx, cy), (radius, radius), 
                    self.pulse_phase * 50, 0, 270, color, 2)
