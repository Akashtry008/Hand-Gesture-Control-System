# Developer Guide - Hand Gesture System

## 🏗️ Architecture Overview

The system follows a clean pipeline: **Input → Detection → Smoothing → Classification → Action → Output**

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Camera         Perception        Intent          Control   │
│  Input          Layer             Layer           Layer     │
│    │                │                │                │      │
│    ├─→ VideoCapture │                │                │      │
│         (OpenCV)    │                │                │      │
│                     │                │                │      │
│                     ├─→ HandTracker  │                │      │
│                     │   (MediaPipe)  │                │      │
│                     │                │                │      │
│                     ├─→ OneEuroFilter│                │      │
│                     │   (Smoothing)  │                │      │
│                     │                ├─→ Classifier   │      │
│                     │                │   (Gesture ID) │      │
│                     │                │                ├─→ PyAutoGUI
│                     │                │                │   (Moves)
│                     │                │                │      │
│                     └────────────────┼────────────────┘      │
│                                      │                       │
│                     ┌────────────────┴────────┐              │
│                     │        HUD Layer        │              │
│                     │    (Visual Feedback)    │              │
│                     └────────────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Module Structure

### `gesture_v3/config.py`
**Purpose**: Centralized configuration
**Key Settings**:
- Physics: `BASE_SENSITIVITY`, `ACCELERATION_FACTOR`
- Smoothing: `ONE_EURO_MIN_CUTOFF`, `ONE_EURO_BETA`
- Gestures: `PINCH_THRESHOLD_NORM`, `CLICK_COOLDOWN`
- Colors: UI color scheme

**To Modify**: Edit values directly, changes take effect on restart

### `gesture_v3/core/system.py`
**Purpose**: Main application loop orchestration
**Methods**:
- `__init__()` - Initialize camera and tracker
- `run()` - Main event loop
- `_process_hand_detected()` - Process detected hand data
- `_execute_gesture()` - Execute gesture-based actions
- `_handle_drag_toggle()` - Drag mode logic
- `_handle_scroll()` - Scroll gesture handling
- `_process_hand_lost()` - Safety when hand disappears

**To Modify**: Add new states or gestures in `_execute_gesture()`

### `gesture_v3/perception/tracker.py`
**Purpose**: MediaPipe hand detection wrapper
**Key Methods**:
- `__init__()` - Load model and initialize
- `process()` - Detect hand landmarks in frame

**To Modify**: Change detection confidence in `HandLandmarkerOptions`

### `gesture_v3/perception/smoothing.py`
**Purpose**: OneEuro filter for jitter reduction
**Key Methods**:
- `smoothing_factor()` - Calculate exponential smoothing coefficient
- `exponential_smoothing()` - Apply smoothing
- `__call__()` - Filter new value

**To Modify**: Adjust `min_cutoff` and `beta` in config for different smoothing

### `gesture_v3/intent/classifier.py`
**Purpose**: Gesture recognition and state classification
**Methods**:
- `process()` - Classify landmarks into gesture
- `_check_hand_stability()` - Measure hand motion
- `_get_finger_states()` - Determine which fingers are up
- `_classify_gesture()` - Determine final gesture state

**Gesture States**:
- `IDLE` - No clear gesture
- `MOVE` - Open palm (cursor move)
- `CLICK_LEFT` - Thumb + index pinch
- `CLICK_RIGHT` - Thumb + middle pinch
- `SCROLL` - Peace sign
- `FIST` - Closed hand (drag toggle)

**To Add New Gesture**:
1. Add finger state check in `_get_finger_states()`
2. Add classification logic in `_classify_gesture()`
3. Add handling in `system.py` `_execute_gesture()`

### `gesture_v3/control/mouse_physics.py`
**Purpose**: Convert gesture to cursor movement with physics
**Key Methods**:
- `update_relative()` - Apply physics and move cursor
- `set_fast_mode()` - Toggle speed boost

**Physics Components**:
- Dead zone: Filter tremors
- Smoothing: Exponential moving average
- Acceleration: Speed based on hand velocity
- Clipping: Cap maximum speed

**To Modify**: Adjust physics constants in config.py

### `gesture_v3/ui/hud.py`
**Purpose**: Visual feedback and HUD rendering
**Methods**:
- `draw()` - Main drawing dispatch
- `_get_hand_center()` - Calculate display point
- `_draw_trail()` - Draw hand movement history
- `_draw_state_indicator()` - State-specific visuals

**To Customize**: Modify drawing in `_draw_state_indicator()` for new states

## 🔧 Common Modifications

### Add a New Gesture

1. **Define in classifier.py**:
```python
def _classify_gesture(self, fingers_up, dist_click, dist_right, is_stable):
    # ... existing gestures ...
    
    # NEW GESTURE
    is_thumbs_up = fingers_up[0] and not any(fingers_up[1:])
    if is_thumbs_up and dist_from_palm > 0.1:
        return "THUMBS_UP"
```

2. **Handle in system.py**:
```python
def _execute_gesture(self, state, delta_x, delta_y, dt, cursor, current_time, norm_x, norm_y):
    # ... existing handlers ...
    
    elif state == "THUMBS_UP":
        pyautogui.press('enter')  # Or any action
```

3. **Add UI indicator in hud.py**:
```python
def _draw_state_indicator(self, img, state, cx, cy):
    # ... existing states ...
    
    elif state == "THUMBS_UP":
        color = (0, 165, 255)  # Orange
        cv2.putText(img, "👍", (cx, cy), ...)
```

### Change Cursor Responsiveness

**In config.py**:
```python
# More responsive (faster)
BASE_SENSITIVITY = 6.0           # Increase from 4.5
ACCELERATION_FACTOR = 20.0       # Increase from 16.0
ONE_EURO_MIN_CUTOFF = 0.8       # Increase from 0.5

# Smoother (slower)
BASE_SENSITIVITY = 3.0           # Decrease from 4.5
ACCELERATION_FACTOR = 10.0       # Decrease from 16.0
ONE_EURO_MIN_CUTOFF = 0.3       # Decrease from 0.5
```

### Change Gesture Sensitivity

**In config.py**:
```python
# Easier clicking (larger pinch distance allowed)
PINCH_THRESHOLD_NORM = 0.12      # Increase from 0.08

# Harder clicking (exact pinch needed)
PINCH_THRESHOLD_NORM = 0.05      # Decrease from 0.08
```

### Add Hand Landmarks Drawing

**In hud.py**:
```python
def draw(self, img, hand_landmarks, state, confidence):
    # Add after existing code:
    if hand_landmarks:
        h, w, _ = img.shape
        for i, lm in enumerate(hand_landmarks):
            x = int(lm.x * w)
            y = int(lm.y * h)
            cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
            cv2.putText(img, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0))
```

## 🐛 Debugging Tips

### Check Gesture State
Add to `system.py` `_execute_gesture()`:
```python
print(f"State: {state}, Confidence: {confidence}, Position: ({norm_x:.2f}, {norm_y:.2f})")
```

### Check Frame Rate
Current FPS is displayed on screen. Target is 60 FPS.

### Check Hand Detection
If hand landmarks are None:
- Verify model file exists
- Check lighting conditions
- Ensure camera access isn't blocked

### Performance Profiling
```python
import time
start = time.time()
# ... code to profile ...
print(f"Took: {time.time() - start:.3f}s")
```

## 📈 Performance Optimization

1. **Reduce Gesture Complexity**: Fewer finger checks = faster classification
2. **Lower Resolution**: Reduce camera resolution if CPU-bound
3. **Increase FPS Target**: Set `TARGET_FPS = 30` for slower systems
4. **Disable HUD**: Skip drawing to improve performance
5. **Reduce Smoothing**: Increase `ONE_EURO_BETA` for faster processing

## 🧪 Testing

### Unit Test Example
```python
from gesture_v3.intent.classifier import GestureClassifier

classifier = GestureClassifier()

# Mock landmarks
class MockLandmark:
    def __init__(self, x, y):
        self.x, self.y = x, y

landmarks = [MockLandmark(0.5, 0.5) for _ in range(21)]

# Test
state, meta = classifier.process(landmarks)
print(f"State: {state}")
```

## 📚 Key Classes

### MediaPipe Landmark
```python
# From MediaPipe
landmark.x      # X position (0-1 normalized)
landmark.y      # Y position (0-1 normalized)
landmark.z      # Z position (depth, -1 to 1)
```

### Gesture State Machine
```
IDLE
├─→ MOVE (open palm)
│   ├─→ CLICK_LEFT (pinch index)
│   ├─→ CLICK_RIGHT (pinch middle)
│   └─→ SCROLL (peace sign)
├─→ FIST (closed hand) → DRAG_ACTIVE
└─→ No hand detected
```

## 🔐 Safety Features

1. **Failsafe FPS**: If FPS drops below threshold, system pauses
2. **Drag Safety**: If hand lost during drag, automatically drops
3. **Cooldowns**: Prevents accidental double-clicks
4. **Dead Zone**: Filters hand tremors

## 📊 Landmark Indices (Hand)

```
Thumb:      0 (wrist), 1, 2, 3, 4 (tip)
Index:      0, 5, 6, 7, 8 (tip)
Middle:     0, 9, 10, 11, 12 (tip)
Ring:       0, 13, 14, 15, 16 (tip)
Pinky:      0, 17, 18, 19, 20 (tip)
```

## 🚀 Best Practices

1. **Always check bounds**: Verify array indices before access
2. **Use config for tuning**: Don't hardcode numbers
3. **Keep methods focused**: Each method does one thing
4. **Add comments for complex logic**: Especially in classifier
5. **Test with real hands**: Simulator can't replace real testing
6. **Version your changes**: Keep working backup

---

**Need Help?**
- See README.md for user guide
- Check QUICK_START.md for basics
- Review comments in source code
- Test incrementally before major changes

Happy coding! 🚀
