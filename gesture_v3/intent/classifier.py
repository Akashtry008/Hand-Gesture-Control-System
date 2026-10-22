import time
import math
from gesture_v3 import config

class GestureClassifier:
    """
    Recognizes comprehensive 1-hand and 2-hand (bimanual) gestures from MediaPipe landmarks.
    """
    def __init__(self):
        self.state = "IDLE"
        self.dual_state = "IDLE"
        self.last_update = time.time()
        
        # Temporal tracking for dynamic gestures
        self.prev_index_z = None
        self.prev_wrist = None
        self.prev_dual_dist = None
        self.prev_dual_angle = None
        self.prev_dual_slider_y = None
        self.last_air_tap_time = 0

    def process(self, landmarks):
        """Backward compatibility alias for process_single"""
        return self.process_single(landmarks)

    def process_single(self, landmarks):
        """
        Analyze single hand landmarks and return gesture state with metadata.
        Returns: (state_string, metadata_dict)
        """
        if not landmarks:
            self.state = "IDLE"
            return self.state, {}

        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Key landmarks
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        index_mcp = landmarks[5]
        thumb_ip = landmarks[3]

        # Euclidean distances between thumb and finger tips
        dist_index_pinch = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
        dist_middle_pinch = math.hypot(thumb_tip.x - middle_tip.x, thumb_tip.y - middle_tip.y)
        dist_ring_pinch = math.hypot(thumb_tip.x - ring_tip.x, thumb_tip.y - ring_tip.y)

        # Finger extension states [thumb, index, middle, ring, pinky]
        fingers_up = self._get_finger_states(landmarks)

        # Air Tap (3D forward push detection on index finger)
        is_air_tap = False
        if self.prev_index_z is not None and dt > 0:
            dz = index_tip.z - self.prev_index_z
            z_vel = dz / dt
            if (z_vel < config.AIR_TAP_Z_VELOCITY and 
                fingers_up[1] and not any(fingers_up[2:]) and 
                (current_time - self.last_air_tap_time) > config.AIR_TAP_COOLDOWN):
                is_air_tap = True
                self.last_air_tap_time = current_time
        self.prev_index_z = index_tip.z

        # Classify gesture based on priority
        state = self._classify_single_gesture(
            landmarks, fingers_up, dist_index_pinch, dist_middle_pinch, dist_ring_pinch, is_air_tap
        )
        self.state = state

        meta = {
            "confidence": 1.0,
            "dist_pinch": dist_index_pinch,
            "fingers_up": fingers_up,
            "wrist": (wrist.x, wrist.y)
        }
        return state, meta

    def process_dual(self, hand_left, hand_right):
        """
        Analyze two hands (left and right on screen) for bimanual gestures.
        Returns: (dual_state, metadata_dict)
        """
        if not hand_left or not hand_right:
            self.dual_state = "NONE"
            self.prev_dual_dist = None
            self.prev_dual_angle = None
            return self.dual_state, {}

        # Centers of both hands (palm center average of wrist, index MCP, pinky MCP)
        c_left_x = (hand_left[0].x + hand_left[5].x + hand_left[17].x) / 3.0
        c_left_y = (hand_left[0].y + hand_left[5].y + hand_left[17].y) / 3.0

        c_right_x = (hand_right[0].x + hand_right[5].x + hand_right[17].x) / 3.0
        c_right_y = (hand_right[0].y + hand_right[5].y + hand_right[17].y) / 3.0

        # Distance between hands
        curr_dist = math.hypot(c_right_x - c_left_x, c_right_y - c_left_y)
        wrist_dist = math.hypot(hand_left[0].x - hand_right[0].x, hand_left[0].y - hand_right[0].y)

        # Angle between hands (radians)
        curr_angle = math.atan2(c_right_y - c_left_y, c_right_x - c_left_x)

        fingers_left = self._get_finger_states(hand_left)
        fingers_right = self._get_finger_states(hand_right)

        state = "NONE"
        meta = {
            "dist": curr_dist,
            "wrist_dist": wrist_dist,
            "angle": curr_angle,
            "center_left": (c_left_x, c_left_y),
            "center_right": (c_right_x, c_right_y)
        }

        # 1. CLAP GESTURE (Hands meet quickly or wrist distance very small)
        if wrist_dist < config.CLAP_DISTANCE_THRESHOLD or curr_dist < 0.08:
            state = "CLAP"
            self.dual_state = state
            return state, meta

        # 2. SCREENSHOT FRAME GESTURE (L-Frame Box formed by thumbs and index fingers)
        is_left_l = fingers_left[0] and fingers_left[1] and not any(fingers_left[2:])
        is_right_l = fingers_right[0] and fingers_right[1] and not any(fingers_right[2:])
        if is_left_l and is_right_l and 0.12 < curr_dist < 0.65:
            # Check if index fingers are pointing opposite or complementary
            state = "FRAME_CAPTURE"
            self.dual_state = state
            return state, meta

        # 3. DUAL VOLUME SLIDER (Left hand is fist anchor, Right hand index moves up/down)
        is_left_fist = not any(fingers_left[1:])
        is_right_pointing = fingers_right[1] and not any(fingers_right[2:])
        if is_left_fist and is_right_pointing:
            right_index_y = hand_right[8].y
            if self.prev_dual_slider_y is not None:
                dy = right_index_y - self.prev_dual_slider_y
                if dy < -0.015:
                    state = "DUAL_VOL_UP"
                elif dy > 0.015:
                    state = "DUAL_VOL_DOWN"
                else:
                    state = "DUAL_SLIDER_IDLE"
            else:
                state = "DUAL_SLIDER_IDLE"
            self.prev_dual_slider_y = right_index_y
            self.dual_state = state
            return state, meta
        else:
            self.prev_dual_slider_y = None

        # 4. TWO-HAND ZOOM (Both hands open or index pinching, moving closer or further apart)
        both_open = all(fingers_left) and all(fingers_right)
        both_pinched = (math.hypot(hand_left[4].x - hand_left[8].x, hand_left[4].y - hand_left[8].y) < 0.10 and
                        math.hypot(hand_right[4].x - hand_right[8].x, hand_right[4].y - hand_right[8].y) < 0.10)

        if (both_open or both_pinched) and self.prev_dual_dist is not None:
            delta_d = curr_dist - self.prev_dual_dist
            if delta_d > config.ZOOM_DELTA_THRESHOLD:
                state = "TWO_HAND_ZOOM_IN"
            elif delta_d < -config.ZOOM_DELTA_THRESHOLD:
                state = "TWO_HAND_ZOOM_OUT"

        # 5. TWO-HAND ROTATE (Angle changes between hands while held out)
        if state == "NONE" and (both_open or (fingers_left[1] and fingers_right[1])) and self.prev_dual_angle is not None:
            delta_angle = curr_angle - self.prev_dual_angle
            # Normalize to [-pi, pi]
            delta_angle = (delta_angle + math.pi) % (2 * math.pi) - math.pi
            if delta_angle > config.ROTATE_DELTA_THRESHOLD:
                state = "TWO_HAND_ROTATE_CW"
            elif delta_angle < -config.ROTATE_DELTA_THRESHOLD:
                state = "TWO_HAND_ROTATE_CCW"

        # 6. WINDOW MAXIMIZE / MINIMIZE (Outward or Inward Push)
        if state == "NONE" and both_open and self.prev_dual_dist is not None:
            delta_d = curr_dist - self.prev_dual_dist
            if delta_d > 0.045:
                state = "WINDOW_MAX"
            elif delta_d < -0.045:
                state = "WINDOW_MIN"

        self.prev_dual_dist = curr_dist
        self.prev_dual_angle = curr_angle
        self.dual_state = state
        return state, meta

    def _get_finger_states(self, landmarks):
        """
        Determines whether each of the 5 fingers is extended.
        Uses distance from wrist combined with screen orientation for robust detection.
        Returns: [thumb_out, index_up, middle_up, ring_up, pinky_up]
        """
        wrist = landmarks[0]
        fingers_up = [False] * 5

        # Tips: [8, 12, 16, 20], PIP joints: [6, 10, 14, 18], MCP joints: [5, 9, 13, 17]
        for i, tip_idx in enumerate([8, 12, 16, 20]):
            pip_idx = tip_idx - 2
            mcp_idx = tip_idx - 3
            
            d_tip = math.hypot(landmarks[tip_idx].x - wrist.x, landmarks[tip_idx].y - wrist.y)
            d_pip = math.hypot(landmarks[pip_idx].x - wrist.x, landmarks[pip_idx].y - wrist.y)
            d_mcp = math.hypot(landmarks[mcp_idx].x - wrist.x, landmarks[mcp_idx].y - wrist.y)
            
            # Rotation-invariant distance check: extended if tip is farther from wrist than PIP and MCP
            dist_extended = (d_tip > d_pip * 1.04) and (d_tip > d_mcp * 1.10)
            
            # Screen-Y check for upright hands: tip is higher up on screen than PIP joint
            y_extended = (landmarks[tip_idx].y < landmarks[pip_idx].y) and (d_tip > d_mcp * 1.02)
            
            fingers_up[i + 1] = dist_extended or y_extended

        # Thumb extension: check distance from pinky MCP (17), index MCP (5), and wrist (0)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        pinky_mcp = landmarks[17]
        index_mcp = landmarks[5]

        d_thumb_pinky = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
        d_thumb_index = math.hypot(thumb_tip.x - index_mcp.x, thumb_tip.y - index_mcp.y)
        d_thumb_wrist = math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y)
        d_mcp_wrist = math.hypot(thumb_mcp.x - wrist.x, thumb_mcp.y - wrist.y)
        
        # Extended if sticking out from palm and farther from wrist than thumb MCP
        fingers_up[0] = (d_thumb_pinky > 0.12 or d_thumb_index > 0.07) and (d_thumb_wrist > d_mcp_wrist * 1.05)

        return fingers_up

    def _classify_single_gesture(self, landmarks, fingers_up, dist_click, dist_right, dist_middle, is_air_tap):
        """Classify single-hand gesture with strict prioritization and responsive air mouse support"""
        thumb_up = fingers_up[0]
        index_up = fingers_up[1]
        middle_up = fingers_up[2]
        ring_up = fingers_up[3]
        pinky_up = fingers_up[4]

        # Landmark references
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        index_tip = landmarks[8]
        index_mcp = landmarks[5]

        # 1. 3D Air Tap (Forward push)
        if is_air_tap:
            return "AIR_TAP"

        # 2. Closed Fist / Thumb Volume Control (All 4 fingers curled into palm)
        # Evaluated before pinches so curled fingertips resting in palm never trigger false clicks
        if not any(fingers_up[1:]):
            # Thumb straight UP -> Volume Up
            if thumb_tip.y < thumb_ip.y - 0.02 and thumb_tip.y < wrist.y - 0.05:
                return "VOL_UP"
            # Thumb straight DOWN -> Volume Down
            elif thumb_tip.y > thumb_ip.y + 0.02 and thumb_tip.y > wrist.y + 0.05:
                return "VOL_DOWN"
            # Closed Fist -> Drag & Drop toggle
            else:
                return "FIST"

        # 3. Pinch Clicks
        # Left click: Thumb + Index pinch (requires index finger to be extended)
        if dist_click < config.PINCH_THRESHOLD_NORM and index_up:
            return "CLICK_LEFT"
            
        # Right click: Thumb + Middle pinch (requires middle finger to be extended)
        if dist_right < config.PINCH_THRESHOLD_NORM and middle_up:
            return "CLICK_RIGHT"
            
        # Middle click: Thumb + Ring pinch (requires ring finger to be extended)
        if dist_middle < config.PINCH_THRESHOLD_NORM and ring_up:
            return "CLICK_MIDDLE"

        # 4. Pinky Promise (Pinky only up, others curled) -> Mute / Unmute
        if pinky_up and not index_up and not middle_up and not ring_up:
            return "MUTE"

        # 5. Spider-Man / Rock-on (Thumb, Index, Pinky extended, Middle & Ring curled) -> Show Desktop
        if thumb_up and index_up and pinky_up and not middle_up and not ring_up:
            return "SHOW_DESKTOP"

        # 6. Four Fingers Up (Index, Middle, Ring, Pinky UP, Thumb tucked across palm) -> App Switcher (Alt + Tab)
        if index_up and middle_up and ring_up and pinky_up and not thumb_up:
            return "ALT_TAB"

        # 7. Peace Sign (Index & Middle UP, Ring & Pinky curled) -> Scroll Mode
        if index_up and middle_up and not ring_up and not pinky_up:
            dx = index_tip.x - wrist.x
            dy = index_tip.y - wrist.y
            if abs(dx) > abs(dy) * 1.3:
                return "SCROLL_H"
            return "SCROLL_V"

        # 8. Gun Gesture (Thumb UP + Index pointing horizontal, Middle & Ring curled) -> Media Track Switch
        if index_up and thumb_up and not middle_up and not ring_up and not pinky_up:
            thumb_is_up = thumb_tip.y < thumb_ip.y - 0.01
            dx = index_tip.x - index_mcp.x
            dy = index_tip.y - index_mcp.y
            if thumb_is_up and abs(dx) > abs(dy) * 1.3 and abs(dx) > 0.08:
                return "NEXT_TRACK" if dx > 0 else "PREV_TRACK"

        # 9. Three Fingers Up (Index, Middle, Ring UP, Pinky curled) -> Play / Pause Media
        if index_up and middle_up and ring_up and not pinky_up:
            return "PLAY_PAUSE"

        # 10. Mouse Movement (Open Palm or Index-Finger Air Pointer)
        # Any extended index finger (pointing) or open palm moves the cursor smoothly
        if index_up or all(fingers_up) or (index_up and middle_up and ring_up):
            return "MOVE"

        return "IDLE"
