import time
import math
from gesture_v3 import config

class GestureClassifier:
    """
    Recognizes hand gestures from landmarks and returns gesture state with confidence.
    """
    def __init__(self):
        self.state = "IDLE"
        self.pinch_confidence = 0.0
        self.last_update = time.time()
        
        # Landmark indices
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20

    def process(self, landmarks):
        """
        Analyze hand landmarks and determine gesture state.
        Returns: (state_string, metadata_dict)
        """
        if not landmarks:
            self.state = "IDLE"
            self.pinch_confidence = 0.0
            return self.state, {}

        # Calculate key distances
        thumb = landmarks[4]
        index = landmarks[8]
        middle = landmarks[12]
        
        dist_click = math.hypot(thumb.x - index.x, thumb.y - index.y)
        dist_right = math.hypot(thumb.x - middle.x, thumb.y - middle.y)
        
        # Check hand stability by measuring wrist velocity
        is_stable = self._check_hand_stability(landmarks)
        
        # Determine finger states (up or down)
        fingers_up = self._get_finger_states(landmarks)
        
        # Classify gesture based on finger positions and pinches
        self.state = self._classify_gesture(fingers_up, dist_click, dist_right, is_stable)
        
        return self.state, {"confidence": 1.0, "pinch_dist": dist_click}
    
    def _check_hand_stability(self, landmarks):
        """Measure wrist motion to determine if hand is stable for clicking"""
        wrist = landmarks[0]
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        if not hasattr(self, 'prev_wrist'):
            self.prev_wrist = wrist
            return True
        
        dx = wrist.x - self.prev_wrist.x
        dy = wrist.y - self.prev_wrist.y
        dist_move = math.hypot(dx, dy)
        
        velocity = dist_move / dt if dt > 0 else 0
        self.prev_wrist = wrist
        
        return velocity < 2.0
    
    def _get_finger_states(self, landmarks):
        """Returns list of boolean values indicating if each finger is up"""
        fingers_up = [False] * 5
        
        # Check if index, middle, ring, and pinky are up
        # Compare tip Y to PIP Y (joint one level down)
        for i, tip_idx in enumerate([8, 12, 16, 20]):
            pip_idx = tip_idx - 2
            fingers_up[i + 1] = landmarks[tip_idx].y < landmarks[pip_idx].y
        
        # Check if thumb is extended (far from index MCP)
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        thumb_out = math.hypot(thumb_tip.x - index_mcp.x, thumb_tip.y - index_mcp.y) > 0.05
        fingers_up[0] = thumb_out
        
        return fingers_up
    
    def _classify_gesture(self, fingers_up, dist_click, dist_right, is_stable):
        """Classify gesture based on finger states and distances"""
        # Check basic hand positions
        is_fist = not any(fingers_up[1:])  # All 4 fingers down
        is_palm = all(fingers_up)  # All fingers up
        is_peace = (fingers_up[1] and fingers_up[2] and 
                   not fingers_up[3] and not fingers_up[4])  # Peace sign
        
        # Priority: Pinch > Scroll > Fist > Palm > Idle
        if dist_click < config.PINCH_THRESHOLD_NORM:
            return "CLICK_LEFT"
        elif dist_right < config.PINCH_THRESHOLD_NORM:
            return "CLICK_RIGHT"
        elif is_peace:
            return "SCROLL"
        elif is_fist:
            return "FIST"
        elif is_palm:
            return "MOVE"
        else:
            return "IDLE"
