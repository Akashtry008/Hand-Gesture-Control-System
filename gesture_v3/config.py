
"""
Centralized configuration for all gesture system settings.
Modify values here to tune behavior without changing code.
"""
import pyautogui

# --- SYSTEM ---
APP_NAME = "Air Interface"
WINDOW_WIDTH, WINDOW_HEIGHT = pyautogui.size()
TARGET_FPS = 60
FAILSAFE_FPS = 15  # Minimum FPS before safety pause

# --- PERCEPTION (Smoothing) ---
# OneEuroFilter parameters for jitter reduction
ONE_EURO_MIN_CUTOFF = 0.5   # Lower = smoother movement
ONE_EURO_BETA = 4.0         # Higher = more responsive
ONE_EURO_D_CUTOFF = 1.0     # Derivative filter cutoff (Hz)

# --- GESTURE DETECTION ---
PINCH_THRESHOLD_NORM = 0.08    # Distance threshold for clicks (normalized)
GESTURE_CONFIDENCE_THRESHOLD = 0.8  # Required confidence for gesture
CONFIDENCE_DECAY = 0.2              # How fast to forget incomplete gestures
CONFIDENCE_GROWTH = 0.15            # How fast to accumulate confidence

# --- CURSOR PHYSICS ---
DEAD_ZONE = 0.001              # Minimum movement to register (prevents tremor)
BASE_SENSITIVITY = 4.5          # Cursor speed multiplier
ACCELERATION_FACTOR = 16.0      # Gain for fast hand movements
MAX_SENSITIVITY = 12.0          # Maximum cursor speed cap
DELTA_SMOOTHING = 0.25          # Exponential smoothing factor

# --- MODES ---
# Fast Mode
FAST_MODE_MULTIPLIER = 1.6      # Speed boost in fast mode
FAST_MODE_SMOOTHING = 0.15      # Less smoothing in fast mode (more responsive)

# --- ACTIONS ---
CLICK_COOLDOWN = 0.35                  # Cooldown between clicks (seconds)
SCROLL_SPEED = 20                      # Scroll pixels per gesture
SCROLL_DEADZONE = 0.05                 # Minimum movement to trigger scroll
DRAG_TOGGLE_COOLDOWN = 1.0             # Cooldown for drag mode toggle

# --- UI COLORS (BGR format for OpenCV) ---
COLOR_IDLE = (255, 255, 0)                  # Cyan (default)
COLOR_MOVE = (255, 255, 255)                # White (open palm)
COLOR_CLICK = (0, 0, 255)                   # Red (left click)
COLOR_RIGHT_CLICK = (255, 0, 0)             # Blue (right click)
COLOR_SCROLL = (255, 0, 255)                # Magenta (scroll mode)
COLOR_DRAG_ACTIVE = (0, 255, 0)             # Green (drag locked)
COLOR_TEXT = (255, 255, 255)                # White (text)
