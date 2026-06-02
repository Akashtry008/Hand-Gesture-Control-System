import math
import pyautogui
from gesture_v3 import config

pyautogui.FAILSAFE = False 

class PhysicsCursor:
    """
    Converts relative hand movement to mouse control with physics effects.
    Applies dead zones, smoothing, and acceleration for natural cursor behavior.
    """
    def __init__(self):
        self.prev_dx = 0.0
        self.prev_dy = 0.0
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        self.fast_mode = False

    def set_fast_mode(self, enabled):
        """Toggle fast mode for boosted cursor speed"""
        self.fast_mode = enabled

    def update_relative(self, dx, dy, dt):
        """
        Update cursor position based on relative hand movement.
        - dx, dy: Hand position change (normalized coordinates)
        - dt: Time delta since last frame
        """
        # 1. Apply dead zone to filter hand tremors
        magnitude = math.hypot(dx, dy)
        if magnitude < config.DEAD_ZONE:
            return 
            
        # 2. Smooth movement delta
        smoothing = config.FAST_MODE_SMOOTHING if self.fast_mode else config.DELTA_SMOOTHING
        alpha = 1.0 - smoothing
        dx = alpha * dx + (1.0 - alpha) * self.prev_dx
        dy = alpha * dy + (1.0 - alpha) * self.prev_dy
        
        self.prev_dx = dx
        self.prev_dy = dy
        
        # 3. Calculate cursor speed with acceleration
        base_speed = config.BASE_SENSITIVITY * (config.FAST_MODE_MULTIPLIER if self.fast_mode else 1.0)
        acceleration = 1.0 + config.ACCELERATION_FACTOR * magnitude
        cursor_speed = base_speed * acceleration
        cursor_speed = min(cursor_speed, config.MAX_SENSITIVITY)
        
        # 4. Convert to screen pixels and apply movement
        move_x = dx * config.WINDOW_WIDTH * cursor_speed
        move_y = dy * config.WINDOW_HEIGHT * cursor_speed
        
        # Accumulate to avoid losing sub-pixel movements
        self.remainder_x += move_x
        self.remainder_y += move_y
        
        int_move_x = int(self.remainder_x)
        int_move_y = int(self.remainder_y)
        
        if int_move_x != 0 or int_move_y != 0:
            pyautogui.move(int_move_x, int_move_y, _pause=False)
            self.remainder_x -= int_move_x
            self.remainder_y -= int_move_y
