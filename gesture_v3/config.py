
"""
Centralized configuration for all gesture system settings.
Modify values here to tune behavior without changing code.
"""
import pyautogui

# --- SYSTEM ---
APP_NAME = "Project Air - Spatial Gesture Control"
WINDOW_WIDTH, WINDOW_HEIGHT = pyautogui.size()
CAMERA_WIDTH = 640          # 640x480 gives 3x to 4x higher FPS and low CPU latency
CAMERA_HEIGHT = 480
TARGET_FPS = 60
FAILSAFE_FPS = 0            # Set to 0: never pause or lock user input on low FPS
ENABLE_AUDIO_FEEDBACK = True  # Subtle audio clicks on actions (Windows winsound)
ENABLE_WEB_BRIDGE = True      # Run local WebSocket/HTTP server for Spatial Node UI
ENABLE_VIRTUAL_CAM = False    # Broadcast frame to Zoom/Teams virtual camera
ENABLE_CLAHE_ENHANCER = False # Disabled by default to preserve maximum FPS on CPU
ENABLE_APP_PROFILES = True    # Context-aware application profiles
WEB_SERVER_PORT = 8765

# --- PERCEPTION (Smoothing) ---
# OneEuroFilter parameters for jitter reduction
ONE_EURO_MIN_CUTOFF = 0.5   # Lower = smoother movement
ONE_EURO_BETA = 4.0         # Higher = more responsive
ONE_EURO_D_CUTOFF = 1.0     # Derivative filter cutoff (Hz)

# --- GESTURE DETECTION THRESHOLDS ---
PINCH_THRESHOLD_NORM = 0.07         # Distance threshold for finger pinches
PINCH_RELEASE_NORM = 0.09           # Distance to release pinch (hysteresis)
DOUBLE_CLICK_INTERVAL = 0.38        # Time window (s) for double click
AIR_TAP_Z_VELOCITY = -0.035         # Forward Z speed for 3D air tap
AIR_TAP_COOLDOWN = 0.45             # Air tap debounce time (s)

# --- CURSOR PHYSICS ---
DEAD_ZONE = 0.0012                  # Minimum movement to register (prevents tremor)
BASE_SENSITIVITY = 4.5              # Cursor speed multiplier
ACCELERATION_FACTOR = 16.0          # Gain for fast hand movements
MAX_SENSITIVITY = 12.0              # Maximum cursor speed cap
DELTA_SMOOTHING = 0.25              # Exponential smoothing factor

# --- MODES ---
FAST_MODE_MULTIPLIER = 1.6          # Speed boost in fast mode
FAST_MODE_SMOOTHING = 0.15          # Less smoothing in fast mode

# --- ACTION COOLDOWNS (Seconds) ---
CLICK_COOLDOWN = 0.28               # Cooldown between left/right/middle clicks
DRAG_TOGGLE_COOLDOWN = 0.8          # Cooldown for fist drag mode toggle
SCROLL_SPEED = 24                   # Scroll pixels per gesture
SCROLL_DEADZONE = 0.015             # Minimum movement to trigger scroll
MEDIA_ACTION_COOLDOWN = 0.6         # Cooldown for play/pause, mute, screenshot
VOLUME_HOLD_COOLDOWN = 0.14         # Cooldown for repeated volume up/down
TRACK_SWITCH_COOLDOWN = 0.8         # Cooldown for next/prev track
HOTKEY_COOLDOWN = 0.85              # Cooldown for Show Desktop, Alt-Tab

# --- TWO-HAND (BIMANUAL) SETTINGS ---
CLAP_DISTANCE_THRESHOLD = 0.09      # Wrist distance normalized for Clap pause
CLAP_COOLDOWN = 1.2                 # Clap cooldown (s)
ZOOM_DELTA_THRESHOLD = 0.018        # Minimum distance change to trigger zoom
ZOOM_COOLDOWN = 0.12                # Cooldown between zoom wheel steps
ROTATE_DELTA_THRESHOLD = 0.08       # Minimum angle change (rad) to trigger rotate
ROTATE_COOLDOWN = 0.20              # Cooldown between rotate steps
WINDOW_SNAP_COOLDOWN = 0.9          # Cooldown for window maximize/minimize
FRAME_BOX_THRESHOLD = 0.15          # Hand distance for screenshot frame

# --- UI COLORS (BGR format for OpenCV) ---
COLOR_IDLE = (255, 255, 0)                  # Cyan
COLOR_MOVE = (255, 255, 255)                # White
COLOR_CLICK = (0, 0, 255)                   # Red (left click)
COLOR_RIGHT_CLICK = (255, 100, 0)           # Blue (right click)
COLOR_MIDDLE_CLICK = (0, 165, 255)          # Orange (middle click)
COLOR_SCROLL = (255, 0, 255)                # Magenta
COLOR_DRAG_ACTIVE = (0, 255, 0)             # Neon Green
COLOR_MEDIA = (0, 215, 255)                 # Gold
COLOR_BIMANUAL = (180, 105, 255)            # Pink/Purple
COLOR_PAUSE = (0, 0, 200)                   # Deep Red
COLOR_TEXT = (255, 255, 255)                # White
