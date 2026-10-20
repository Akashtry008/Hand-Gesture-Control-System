# Hand Gesture Control System - Project Air

> "I am not controlling a computer. The computer understands my intent."

A production-grade hand gesture interface system to control your PC using hand gestures via a webcam. Built with Python, OpenCV, and MediaPipe.

## Features

### Core Capabilities
- **Physics-Based Cursor**: Momentum, friction, and weighted control for stable, jitter-free movement
- **Intent Engine**: Confidence-based gesture detection to prevent accidental clicks
- **Multi-Mode Interaction**: Move, Click, Scroll, Drag, and Fast Mode support
- **Professional Smoothing**: OneEuro filter for professional-grade jitter reduction
- **Real-time Visual Dashboard**: Holographic HUD overlay with finger trails and dynamic reticles

### Gestures Supported (Single-Hand & Two-Hand Bimanual)
See [GESTURE_GUIDE.md](file:///d:/HandGes%20-%20CV/GESTURE_GUIDE.md) for complete visual tutorials and pro-tips.

#### 🖐️ 1-Hand Controls
- **MOVE**: Open palm - Cursor follows with physics momentum & $1€$ smoothing
- **LEFT CLICK**: Pinch Thumb + Index finger
- **DOUBLE CLICK**: Double-tap Thumb + Index pinch within 0.38s
- **3D AIR TAP**: Point Index finger forward toward webcam (contactless push)
- **RIGHT CLICK**: Pinch Thumb + Middle finger
- **MIDDLE CLICK**: Pinch Thumb + Ring finger (open link in new tab)
- **DRAG & DROP**: Make a fist to lock drag; make fist again to release
- **SCROLL (V / H)**: Peace sign ($V$) vertical or tilted sideways for horizontal
- **VOLUME UP / DOWN**: Thumbs Up 👍 / Thumbs Down 👎
- **MUTE / UNMUTE**: Pinky only extended (Pinky Promise 🤙)
- **PLAY / PAUSE**: "OK" sign 👌 (Thumb + Index ring, 3 fingers up)
- **NEXT / PREV TRACK**: Point Index finger horizontally Right 👉 / Left 👈
- **SHOW DESKTOP**: Spider-Man / Rock-on 🤟 (`Win + D`)
- **APP SWITCHER**: Four fingers up ✋ (`Alt + Tab`)

#### 👐 2-Hand Bimanual Controls
- **TWO-HAND ZOOM**: Spread hands apart to **Zoom In**, bring closer to **Zoom Out**
- **TWO-HAND ROTATE**: Rotate hands like a steering wheel to turn canvas/photos
- **SCREENSHOT SNIP**: Form a rectangular frame box $[\ ]$ with thumbs and index fingers
- **TWO-HAND CLAP**: Clap hands together to instant pause/resume tracking
- **WINDOW MAX / MIN**: Push hands outward to maximize; pull inward to minimize
- **DUAL VOLUME SLIDER**: Left fist anchor + Right index vertical slide

#### 🚀 Advanced Next-Gen Modules
- **Interactive Spatial Node Constellation (Point 1)**: Physics-connected node galaxy accessible in browser via `http://127.0.0.1:8765/` or hotkey `'N'`
- **$1 Unistroke AI Macro Recorder (Point 4)**: Trace custom shapes in thin air ("C" for Chrome, "S" for Spotify, circle for F5 refresh)
- **Virtual Camera for Zoom & Teams (Point 5)**: Stream holographic skeletal overlays directly to Zoom/Teams/Meet via `'V'`
- **Context-Aware App Profiles (Point 2)**: Auto-switches controls for Spotify, PowerPoint presentations (laser pointer & slide flipper), and Chrome
- **Air Canvas & Mid-Air Whiteboard (Point 3)**: Draw with neon glowing paint in the air via `'C'`, wipe clean via `'E'`
- **CLAHE Lighting Enhancer (Point 7)**: Contrast adaptive equalization for dim rooms

## Prerequisites

- Python 3.8+
- Webcam (720p or better recommended)
- MediaPipe Hand Landmarker model: `hand_landmarker.task`
- Windows/Mac/Linux with Python support

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download the Hand Landmarker Model
The system requires the MediaPipe hand landmarker model. Download it using:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task -OutFile hand_landmarker.task
```

**Mac/Linux:**
```bash
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### 3. Run the Application
```bash
python main_v3.py
```

## How to Use

### Getting Started
1. Position your webcam to capture your hand clearly
2. Allow the app to detect your hand (you'll see landmarks on screen)
3. Open your palm to move the cursor
4. Pinch thumb + index for left-click
5. Pinch thumb + middle for right-click

### Gesture Tips

#### Move Cursor
- Keep your hand open with fingers relaxed
- Move your hand smoothly - physics smoothing handles jitter
- Stay within the camera's field of view

#### Left Click
- Bring thumb and index finger together
- Distance should be close (< 8mm normalized)
- Hold briefly for detection
- Visual feedback: HUD reticle shrinks and changes color

#### Right Click
- Pinch thumb and middle finger together
- Same distance requirement as left-click
- System differentiates based on which finger is pinched

#### Scroll Mode
- Make a peace sign (Victory V sign)
- Index and middle fingers UP, ring and pinky DOWN
- Move hand UP to scroll up, DOWN to scroll down
- Exit by lowering your middle finger

#### Drag Mode
- Make a fist to enter drag mode
- System automatically holds mouse button down
- Move your hand to drag items
- Make fist again to release

## Configuration

Edit `gesture_v3/config.py` to customize:

### Physics & Smoothing
- `BASE_SENSITIVITY`: Cursor movement speed (default: 4.5)
- `ACCELERATION_FACTOR`: Speed boost for fast movements (default: 16.0)
- `DEAD_ZONE`: Minimum movement to register (prevents hand tremors)
- `ONE_EURO_MIN_CUTOFF`: Lower value = smoother movement (default: 0.5)
- `ONE_EURO_BETA`: Higher value = more responsive (default: 4.0)

### Gesture Settings
- `PINCH_THRESHOLD_NORM`: Distance threshold for click detection (default: 0.08)
- `CLICK_COOLDOWN`: Minimum time between clicks (default: 0.35s)
- `CONFIDENCE_THRESHOLD`: Gesture confidence needed (default: 0.8)
- `GESTURE_CONFIDENCE_DECAY`: How fast to forget a gesture (default: 0.2)

### Display
- `TARGET_FPS`: Target frames per second (default: 60)
- `WINDOW_WIDTH/HEIGHT`: Screen resolution (auto-detected)

## Project Architecture

### Modern V3 Structure (Used)
```
gesture_v3/
├── core/system.py          # Main application loop & orchestration
├── perception/
│   ├── tracker.py          # MediaPipe hand detection wrapper
│   └── smoothing.py        # OneEuroFilter implementation
├── intent/
│   └── classifier.py       # Gesture state machine & confidence system
├── control/
│   └── mouse_physics.py    # Physics-based cursor engine
├── ui/
│   └── hud.py              # Cinematic HUD rendering
└── config.py               # Central configuration
```

### Module Responsibilities
- **core/system.py**: Coordinates all subsystems, handles main event loop
- **perception/tracker.py**: Detects hand landmarks using MediaPipe
- **perception/smoothing.py**: Filters hand position data for smooth movement
- **intent/classifier.py**: Interprets hand poses as gestures with confidence scoring
- **control/mouse_physics.py**: Converts gesture movements to mouse control with physics
- **ui/hud.py**: Renders real-time visual feedback on screen
- **config.py**: Centralized settings for all components

## Troubleshooting

### Hand Not Detected
- Ensure good lighting conditions
- Position hand within camera frame
- Check that `hand_landmarker.task` exists in project root
- Verify camera is not in use by another application

### Jerky Cursor Movement
- Lower `ONE_EURO_BETA` for more smoothing (may reduce responsiveness)
- Increase `DEAD_ZONE` to filter out hand tremors
- Reduce `ACCELERATION_FACTOR` for less aggressive gains

### Clicks Not Registering
- Increase `PINCH_THRESHOLD_NORM` to make clicks easier
- Reduce `CLICK_COOLDOWN` to allow faster clicking
- Move fingers closer together before pinching

### Low Performance / FPS Issues
- Reduce camera resolution in `gesture_v3/config.py`
- Lower `TARGET_FPS` if system is struggling
- Close other CPU-intensive applications
- Update graphics drivers

## Version History

### V3 (Current) - Production Release
- Physics-based cursor with momentum and friction
- Intent confidence engine for reliable gesture detection
- Professional OneEuro smoothing filter
- Cinematic HUD with real-time feedback
- Optimized performance and accuracy

### V2
- Multi-mode interaction (Move/Scroll/Pause)
- Expanded gesture set
- Auto-pause on hand loss or low FPS

### V1
- Basic cursor control with mouse gestures
- Simple click detection
- Foundation for later versions

## System Requirements

- **CPU**: Dual-core processor minimum (2+ GHz)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Camera**: Webcam 1080p or better recommended for accuracy
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Internet**: Required for initial model download

## Tips for Best Results

1. **Good Lighting**: Work in well-lit environments for reliable detection
2. **Camera Angle**: Position camera at eye level for natural hand detection
3. **Hand Visibility**: Keep hand within camera frame and clearly visible
4. **Hand Speed**: Move hand smoothly and deliberately for better tracking
5. **Gesture Hold Time**: Hold pinches for ~0.25 seconds for reliable detection
6. **Calibration**: Let system track your hand for a few seconds before using gestures

## Known Limitations

- Single hand tracking (best accuracy with one hand visible)
- Requires good background contrast for reliable detection
- Performance depends on camera quality and lighting
- May require calibration for different hand sizes

## Advanced Usage

### Fast Mode
Press **'F'** to toggle fast mode for increased cursor sensitivity and responsiveness. Useful for precise clicking on small targets.

### Drag Mode
- Perfect for dragging windows, selecting text, or manipulating files
- Toggle on/off with fist gesture
- Visual indicator shows when drag is active

### Gesture Confidence
The system uses internal confidence scoring to prevent accidental gestures. You can tune this in `config.py` for your preferences.

## Technical Details

### Gesture Detection Pipeline
1. **Capture**: Frame from webcam
2. **Track**: MediaPipe detects 21 hand landmarks
3. **Smooth**: OneEuro filter reduces jitter
4. **Classify**: Intent engine determines gesture with confidence score
5. **Control**: Physics engine converts gesture to mouse movement
6. **Render**: HUD displays state and feedback on screen

### Physics Engine
The cursor uses:
- **Base Sensitivity**: Sets baseline movement speed
- **Acceleration**: Gains increase with hand velocity for responsive control
- **Dead Zone**: Filters out tremors from stationary hands
- **Smoothing**: Exponential moving average for lag reduction

## Contributing & Customization

The modular architecture makes it easy to:
- Customize gesture recognition (modify `classifier.py`)
- Adjust physics behavior (tune `mouse_physics.py`)
- Change visual feedback (edit `hud.py`)
- Add new gestures (extend `classifier.py`)

## License & Credits

*Senior Engineering Project - Gesture Interface System*

Built with:
- [MediaPipe](https://mediapipe.dev/) - Hand detection
- [OpenCV](https://opencv.org/) - Computer vision
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Mouse control
- [NumPy](https://numpy.org/) - Numerical computing

---

*Last Updated: 2026*
*For best results, ensure your environment meets all prerequisites.*
