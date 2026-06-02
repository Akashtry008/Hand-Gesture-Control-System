# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Download Hand Landmarker Model
**Windows (PowerShell)**:
```powershell
Invoke-WebRequest -Uri https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task -OutFile hand_landmarker.task
```

**Mac/Linux**:
```bash
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### 3️⃣ Run Application
```bash
python main_v3.py
```

## 👋 Basic Gestures

| Gesture | Action |
|---------|--------|
| **Open Palm** | Move cursor |
| **Thumb + Index Pinch** | Left click |
| **Thumb + Middle Pinch** | Right click |
| **Peace Sign** + Move | Scroll up/down |
| **Fist** | Toggle drag mode |
| **Press F** | Fast mode (speed boost) |
| **Press Q** | Quit app |

## ⚙️ Quick Tuning

Edit `gesture_v3/config.py`:

**Cursor Too Jumpy?**
```python
ONE_EURO_BETA = 2.0  # Lower from 4.0
```

**Cursor Too Slow?**
```python
BASE_SENSITIVITY = 6.0  # Increase from 4.5
```

**Clicks Not Working?**
```python
PINCH_THRESHOLD_NORM = 0.10  # Increase from 0.08
```

**Hand Shaking/Tremor?**
```python
DEAD_ZONE = 0.005  # Increase from 0.001
```

## 🎯 Tips for Best Results

1. **Good Lighting**: Bright room for accurate detection
2. **Camera Position**: Eye level, 1-2 feet away
3. **Hand Visibility**: Keep hand in frame, clearly visible
4. **Smooth Movements**: Gentle, deliberate hand motion
5. **Gesture Hold**: Hold pinches for ~0.25 seconds

## 🛠️ Troubleshooting

**Hand not detected?**
- Check lighting (too dark = poor detection)
- Ensure hand is in camera frame
- Verify `hand_landmarker.task` exists

**Jerky cursor?**
- Lower `ONE_EURO_BETA` in config
- Increase `DEAD_ZONE` to filter tremor

**Clicks not registering?**
- Pinch fingers closer together
- Increase `PINCH_THRESHOLD_NORM`
- Hold pinch longer

**Poor performance?**
- Close other apps using camera
- Lower camera resolution if needed
- Update graphics drivers

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

## 🎮 Project Structure (Simplified)

```
HandGes/
├── main_v3.py              # Start here
├── gesture_v3/
│   ├── config.py           # Tuning settings
│   ├── core/system.py      # Main loop
│   ├── perception/          # Hand tracking
│   ├── intent/             # Gesture recognition
│   ├── control/            # Physics engine
│   └── ui/                 # Visual feedback
└── hand_landmarker.task    # AI model
```

---

**Ready to use! Enjoy gesture control! 🎉**
