import cv2
import numpy as np
import time

class AirCanvas:
    """
    Virtual Air Canvas & Mid-Air Whiteboard.
    Allows real-time sketching, annotation, and spatial drawing directly on screen.
    """
    PALETTE = [
        ("CYAN", (255, 255, 0)),
        ("GREEN", (0, 255, 0)),
        ("PINK", (255, 0, 255)),
        ("GOLD", (0, 215, 255)),
        ("WHITE", (255, 255, 255))
    ]

    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.is_active = False
        self.color_idx = 0
        self.brush_size = 4
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.prev_pt = None
        self.last_color_cycle = 0.0

    def toggle(self):
        """Toggle drawing canvas mode"""
        self.is_active = not self.is_active
        if not self.is_active:
            self.prev_pt = None
        return self.is_active

    def clear(self):
        """Wipe canvas clean"""
        self.canvas.fill(0)
        self.prev_pt = None

    def cycle_color(self):
        """Cycle to next brush color"""
        now = time.time()
        if now - self.last_color_cycle > 0.4:
            self.color_idx = (self.color_idx + 1) % len(self.PALETTE)
            self.last_color_cycle = now
        return self.PALETTE[self.color_idx][0]

    def get_current_color(self):
        return self.PALETTE[self.color_idx][1]

    def get_current_color_name(self):
        return self.PALETTE[self.color_idx][0]

    def process(self, hand_landmarks, state, hud):
        """Process drawing inputs from index fingertip"""
        if not self.is_active or not hand_landmarks:
            self.prev_pt = None
            return

        # Index fingertip position
        idx_tip = hand_landmarks[8]
        cx = int(idx_tip.x * self.width)
        cy = int(idx_tip.y * self.height)

        # Drawing is active during Left Click pinch or Index pointing with thumb pinched
        is_drawing = (state in ["CLICK_LEFT", "DRAG_ACTIVE"])

        if is_drawing:
            curr_pt = (cx, cy)
            color = self.get_current_color()
            if self.prev_pt is not None:
                # Draw thick anti-aliased glowing stroke
                cv2.line(self.canvas, self.prev_pt, curr_pt, color, self.brush_size, cv2.LINE_AA)
            self.prev_pt = curr_pt
        else:
            self.prev_pt = None

        # Cycle color if Middle pinch
        if state == "CLICK_RIGHT":
            new_col = self.cycle_color()
            hud.trigger_notification(f"🎨 COLOR: {new_col}", self.get_current_color(), duration=0.5)

    def blend(self, img):
        """Blend glowing canvas onto camera frame"""
        if not self.is_active:
            return img

        # Mask of where drawing exists
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Black-out area of drawing in original image, then add drawing
        img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        draw_fg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask)
        blended = cv2.add(img_bg, draw_fg)

        # Top indicator for canvas mode
        col_name, col_bgr = self.PALETTE[self.color_idx]
        cv2.putText(blended, f"[ AIR CANVAS ON: {col_name} ] (Pinch to Draw | 'E' to Erase)", 
                    (self.width // 2 - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col_bgr, 2, cv2.LINE_AA)
        return blended
