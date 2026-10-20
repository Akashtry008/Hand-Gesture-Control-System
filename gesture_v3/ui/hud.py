import cv2
import numpy as np
import time
from collections import deque
from gesture_v3 import config

# MediaPipe 21 hand landmark bone connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]

class CinematicHUD:
    """
    Renders high-tech heads-up display supporting both 1-Hand and 2-Hand (Bimanual) tracking,
    skeletal visualization, dynamic energy beams, and action notification toasts.
    """
    def __init__(self):
        self.trail_primary = deque(maxlen=24)
        self.trail_secondary = deque(maxlen=24)
        self.pulse_phase = 0.0
        self.notification_msg = ""
        self.notification_expire = 0.0
        self.notification_color = (0, 255, 255)

    def trigger_notification(self, message, color=(0, 255, 255), duration=1.4):
        """Display temporary sci-fi notification toast at screen top"""
        self.notification_msg = message
        self.notification_color = color
        self.notification_expire = time.time() + duration

    def draw(self, img, hands_input, state="IDLE", confidence=1.0, dual_state="NONE", is_paused=False, profile="DEFAULT", vcam_active=False):
        """
        Draw comprehensive HUD overlay.
        - hands_input: Single hand landmark list, list of hand landmarks, or None.
        - state: Single-hand gesture state
        - dual_state: Two-hand bimanual state (if active)
        - is_paused: System pause state flag
        - profile: Context-aware app profile (MEDIA, PRESENTATION, BROWSER, DEFAULT)
        - vcam_active: Virtual camera streaming status
        """
        h, w, _ = img.shape
        self.pulse_phase += 0.08

        # Normalize hands_input to a list of hands
        hands = []
        if hands_input is not None:
            if isinstance(hands_input, list) and len(hands_input) > 0:
                if hasattr(hands_input[0], 'x'):  # Single hand: list of landmarks
                    hands = [hands_input]
                elif isinstance(hands_input[0], list):  # Multiple hands
                    hands = hands_input

        # Draw Top HUD Banner (Status & Mode & Profile)
        self._draw_header_bar(img, len(hands), state, dual_state, is_paused, profile, vcam_active)

        # Draw Notification Toast
        self._draw_notification(img, w)

        # Draw Footer Quick Reference
        self._draw_footer(img, w, h)

        if not hands:
            self.trail_primary.clear()
            self.trail_secondary.clear()
            return

        # Render each hand
        centers = []
        for i, hand in enumerate(hands[:2]):
            is_primary = (i == 0)
            trail = self.trail_primary if is_primary else self.trail_secondary
            base_color = (255, 255, 0) if is_primary else (255, 0, 255)  # Cyan vs Magenta
            
            # Draw skeletal bones
            self._draw_hand_skeleton(img, hand, w, h, base_color)
            
            # Center of palm
            cx = int((hand[0].x + hand[5].x + hand[17].x) / 3 * w)
            cy = int((hand[0].y + hand[5].y + hand[17].y) / 3 * h)
            centers.append((cx, cy))
            
            trail.appendleft((cx, cy))
            self._draw_trail(img, trail, base_color)

            # Draw reticle
            active_state = dual_state if (len(hands) > 1 and dual_state != "NONE") else state
            self._draw_reticle(img, cx, cy, active_state, is_primary)

        # If 2 hands detected, draw bimanual connections and guides
        if len(hands) >= 2 and len(centers) >= 2:
            self._draw_bimanual_overlay(img, centers[0], centers[1], dual_state)

    def _draw_hand_skeleton(self, img, landmarks, w, h, color):
        """Draw illuminated bones and glowing landmark joints"""
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        
        # Draw bones
        for p1_idx, p2_idx in HAND_CONNECTIONS:
            cv2.line(img, pts[p1_idx], pts[p2_idx], (int(color[0]*0.4), int(color[1]*0.4), int(color[2]*0.4)), 1, cv2.LINE_AA)
            cv2.line(img, pts[p1_idx], pts[p2_idx], color, 1)

        # Draw joints
        for i, pt in enumerate(pts):
            radius = 4 if i in [4, 8, 12, 16, 20] else 2
            cv2.circle(img, pt, radius, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(img, pt, radius + 1, color, 1, cv2.LINE_AA)

    def _draw_trail(self, img, trail, color):
        """Draw motion trail for hand movement"""
        for i in range(1, len(trail)):
            thickness = max(1, int(np.sqrt(len(trail) / i) * 1.8))
            alpha_color = tuple(int(c * (1.0 - i / len(trail))) for c in color)
            cv2.line(img, trail[i-1], trail[i], alpha_color, thickness, cv2.LINE_AA)

    def _draw_reticle(self, img, cx, cy, state, is_primary):
        """Draw dynamic state-reactive reticle"""
        radius = int(32 + np.sin(self.pulse_phase) * 4)
        color = config.COLOR_IDLE
        
        if state == "MOVE":
            color = config.COLOR_MOVE
            radius = 22
        elif state == "FAST_MOVE":
            color = (0, 255, 255)
            radius = 24
        elif state in ["CLICK_LEFT", "AIR_TAP"]:
            color = config.COLOR_CLICK
            radius = 38
            cv2.circle(img, (cx, cy), radius, color, 3, cv2.LINE_AA)
        elif state == "CLICK_RIGHT":
            color = config.COLOR_RIGHT_CLICK
            radius = 36
            cv2.putText(img, "R", (cx - 8, cy + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        elif state == "CLICK_MIDDLE":
            color = config.COLOR_MIDDLE_CLICK
            radius = 36
            cv2.putText(img, "M", (cx - 8, cy + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        elif state == "DRAG_ACTIVE":
            color = config.COLOR_DRAG_ACTIVE
            radius = 38
            cv2.rectangle(img, (cx - 12, cy - 12), (cx + 12, cy + 12), color, -1)
        elif state in ["SCROLL_V", "SCROLL_H"]:
            color = config.COLOR_SCROLL
            radius = 42
            if state == "SCROLL_V":
                cv2.arrowedLine(img, (cx, cy - 10), (cx, cy - 40), color, 2, cv2.LINE_AA)
                cv2.arrowedLine(img, (cx, cy + 10), (cx, cy + 40), color, 2, cv2.LINE_AA)
            else:
                cv2.arrowedLine(img, (cx - 10, cy), (cx - 40, cy), color, 2, cv2.LINE_AA)
                cv2.arrowedLine(img, (cx + 10, cy), (cx + 40, cy), color, 2, cv2.LINE_AA)
        elif state in ["VOL_UP", "VOL_DOWN", "MUTE", "PLAY_PAUSE", "NEXT_TRACK", "PREV_TRACK"]:
            color = config.COLOR_MEDIA
            radius = 40
            cv2.circle(img, (cx, cy), radius, color, 2, cv2.LINE_AA)
        elif "TWO_HAND" in state or state in ["CLAP", "FRAME_CAPTURE"]:
            color = config.COLOR_BIMANUAL
            radius = 42

        # Rotating outer targeting arcs
        start_angle = int((self.pulse_phase * 60) % 360)
        cv2.ellipse(img, (cx, cy), (radius, radius), start_angle, 0, 90, color, 2, cv2.LINE_AA)
        cv2.ellipse(img, (cx, cy), (radius, radius), start_angle + 180, 0, 90, color, 2, cv2.LINE_AA)

    def _draw_bimanual_overlay(self, img, c1, c2, dual_state):
        """Draw dynamic laser connection and bimanual HUD elements between hands"""
        # Connect hands with sci-fi pulse beam
        beam_color = config.COLOR_BIMANUAL
        cv2.line(img, c1, c2, (int(beam_color[0]*0.3), int(beam_color[1]*0.3), int(beam_color[2]*0.3)), 3, cv2.LINE_AA)
        cv2.line(img, c1, c2, beam_color, 1, cv2.LINE_AA)
        
        mid_x = (c1[0] + c2[0]) // 2
        mid_y = (c1[1] + c2[1]) // 2
        dist_px = int(np.hypot(c2[0] - c1[0], c2[1] - c1[1]))

        # Distance tag pill
        cv2.circle(img, (mid_x, mid_y), 6, beam_color, -1)
        cv2.putText(img, f"SPAN: {dist_px}px", (mid_x - 35, mid_y - 12), 
                    cv2.FONT_HERSHEY_PLAIN, 1.0, (220, 220, 255), 1, cv2.LINE_AA)

        # Special visualizer for Frame Capture
        if dual_state == "FRAME_CAPTURE":
            x_min = min(c1[0], c2[0]) - 30
            y_min = min(c1[1], c2[1]) - 30
            x_max = max(c1[0], c2[0]) + 30
            y_max = max(c1[1], c2[1]) + 30
            
            # Draw camera corner brackets
            bracket_len = 25
            c = (0, 255, 255)
            # Top-Left
            cv2.line(img, (x_min, y_min), (x_min + bracket_len, y_min), c, 3)
            cv2.line(img, (x_min, y_min), (x_min, y_min + bracket_len), c, 3)
            # Top-Right
            cv2.line(img, (x_max, y_min), (x_max - bracket_len, y_min), c, 3)
            cv2.line(img, (x_max, y_min), (x_max, y_min + bracket_len), c, 3)
            # Bottom-Left
            cv2.line(img, (x_min, y_max), (x_min + bracket_len, y_max), c, 3)
            cv2.line(img, (x_min, y_max), (x_min, y_max - bracket_len), c, 3)
            # Bottom-Right
            cv2.line(img, (x_max, y_max), (x_max - bracket_len, y_max), c, 3)
            cv2.line(img, (x_max, y_max), (x_max, y_max - bracket_len), c, 3)

            cv2.putText(img, "[ SCREENSHOT VIEW края ]", (x_min + 10, y_min - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, c, 2, cv2.LINE_AA)

    def _draw_header_bar(self, img, hand_count, state, dual_state, is_paused, profile="DEFAULT", vcam_active=False):
        """Draw top cyberpunk status bar with profile and virtual cam tags"""
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (img.shape[1], 46), (15, 15, 25), -1)
        cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)

        # Mode label
        if is_paused:
            mode_text = "[ SYSTEM PAUSED ]"
            mode_color = config.COLOR_PAUSE
        elif hand_count >= 2:
            mode_text = "[ 2-HAND BIMANUAL MODE ]"
            mode_color = config.COLOR_BIMANUAL
        elif hand_count == 1:
            mode_text = "[ 1-HAND AIR MOUSE ]"
            mode_color = config.COLOR_IDLE
        else:
            mode_text = "[ SCANNING FOR HANDS ]"
            mode_color = (120, 120, 120)

        cv2.putText(img, mode_text, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.60, mode_color, 2, cv2.LINE_AA)

        # Context-Aware Profile Badge
        if profile and profile != "DEFAULT":
            p_text = f"PROFILE: {profile}"
            cv2.putText(img, p_text, (img.shape[1] // 2 - 100, 28), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 200), 2, cv2.LINE_AA)

        # Virtual Cam status indicator
        if vcam_active:
            cv2.putText(img, "● V-CAM LIVE", (img.shape[1] // 2 + 80, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 2, cv2.LINE_AA)

        # Active State Pill
        disp_state = dual_state if (hand_count >= 2 and dual_state != "NONE") else state
        state_str = f"ACTIVE: {disp_state}"
        cv2.putText(img, state_str, (img.shape[1] - 280, 28), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA)

    def _draw_notification(self, img, w):
        """Draw temporary action alert toast (e.g. Volume Up, Snip, Desktop)"""
        now = time.time()
        if now < self.notification_expire and self.notification_msg:
            alpha = min(1.0, (self.notification_expire - now) / 0.3)
            box_w = 380
            x1 = (w - box_w) // 2
            x2 = x1 + box_w
            y1 = 56
            y2 = 98

            overlay = img.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 30, 40), -1)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), self.notification_color, 2)
            cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

            # Center text
            text_size = cv2.getTextSize(self.notification_msg, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)[0]
            tx = x1 + (box_w - text_size[0]) // 2
            ty = y1 + 28
            cv2.putText(img, self.notification_msg, (tx, ty), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.notification_color, 2, cv2.LINE_AA)

    def _draw_footer(self, img, w, h):
        """Draw bottom helper command cheat sheet"""
        overlay = img.copy()
        cv2.rectangle(overlay, (0, h - 30), (w, h), (10, 10, 15), -1)
        cv2.addWeighted(overlay, 0.70, img, 0.30, 0, img)

        footer_text = "HOTKEYS: [Q] Quit | [F] Fast | [C] Air Canvas | [V] VirtCam | [R] Macro REC | [N] Node Matrix"
        cv2.putText(img, footer_text, (20, h - 10), 
                    cv2.FONT_HERSHEY_PLAIN, 0.95, (180, 180, 200), 1, cv2.LINE_AA)
