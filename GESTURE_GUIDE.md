# 🖐️ Comprehensive Gesture Guide - Project Air

> Complete reference manual for **Single-Hand (Air Mouse & Media)** and **Two-Hand (Bimanual Spatial Computing)** gesture controls.

---

## 📋 Table of Contents
1. [Can We Use Both 1-Hand and 2-Hand Gestures?](#-dual-mode-architecture)
2. [Single-Hand Gestures (14 Gestures)](#-single-hand-gestures)
   - [1. Mouse Movement (Open Palm or Index-Finger Air Pointer)](#1-mouse-movement-open-palm-or-index-finger-air-pointer)
   - [2. Left Click (Index Pinch)](#2-left-click-index-pinch)
   - [3. Double Click (Double Pinch)](#3-double-click-double-pinch)
   - [4. 3D Air Tap (Push-to-Click)](#4-3d-air-tap-push-to-click)
   - [5. Right Click (Middle Pinch)](#5-right-click-middle-pinch)
   - [6. Middle Click / New Tab (Ring Pinch)](#6-middle-click--new-tab-ring-pinch)
   - [7. Drag & Drop (Closed Fist Toggle)](#7-drag--drop-closed-fist-toggle)
   - [8. Vertical Scroll (Peace Sign Up/Down)](#8-vertical-scroll-peace-sign)
   - [9. Horizontal Scroll (Horizontal Peace Sign)](#9-horizontal-scroll-horizontal-peace-sign)
   - [10. Volume Up (Thumbs Up)](#10-volume-up-thumbs-up)
   - [11. Volume Down (Thumbs Down)](#11-volume-down-thumbs-down)
   - [12. Mute / Unmute (Pinky Promise)](#12-mute--unmute-pinky-promise)
   - [13. Play / Pause Media (Three Fingers Up)](#13-play--pause-media-three-fingers-up-)
   - [14. Track Switch Next / Prev (Gun Gesture)](#14-track-switch-next--prev-gun-gesture)
   - [15. Show Desktop (Spider-Man / Rock-On)](#15-show-desktop-spider-man--rock-on)
   - [16. App Switcher / Alt-Tab (Four Fingers)](#16-app-switcher--alt-tab-four-fingers)
3. [Two-Hand Bimanual Gestures (6 Gestures)](#-two-hand-bimanual-gestures)
   - [1. Two-Hand Zoom In / Out (Pinch-to-Scale)](#1-two-hand-zoom-in--out)
   - [2. Two-Hand Rotate CW / CCW](#2-two-hand-rotate-cw--ccw)
   - [3. Screenshot Snipping Tool (L-Frame Box)](#3-screenshot-snipping-tool-l-frame-box)
   - [4. Two-Hand Clap (Freeze / Emergency Pause)](#4-two-hand-clap-freeze--emergency-pause)
   - [5. Window Maximize / Minimize (Outward / Inward Push)](#5-window-maximize--minimize)
   - [6. Dual Volume Slider (Fist Anchor + Index Slide)](#6-dual-volume-slider)
4. [Advanced Next-Gen Modules](#-advanced-next-gen-modules)
   - [1. Interactive Spatial Node Constellation (Point 1)](#1-interactive-spatial-node-constellation-point-1)
   - [2. $1 Unistroke Custom Gesture Macro Recorder (Point 4)](#2-1-unistroke-custom-gesture-macro-recorder-point-4)
   - [3. Virtual Camera for Zoom, Teams & Meet (Point 5)](#3-virtual-camera-for-zoom-teams--meet-point-5)
   - [4. Context-Aware Application Profiles (Point 2)](#4-context-aware-application-profiles-air-streamdeck---point-2)
   - [5. Virtual Air Canvas & Mid-Air Whiteboard (Point 3)](#5-virtual-air-canvas--mid-air-whiteboard-point-3)
5. [Master Keyboard Shortcuts & Settings](#%EF%B8%8F-master-keyboard-shortcuts)

---

## ⚡ Dual-Mode Architecture

### **Can we use both 1-hand and 2-hand gestures?**
**YES, seamlessly!**

- **When 1 Hand is Visible**: The system operates in **1-Hand Air Mouse & Multimedia Mode**. You have full desktop navigation, clicks, scrolling, volume, media control, and window switching with just one hand.
- **When 2 Hands Enter the Camera**: The system automatically switches to **2-Hand Bimanual Spatial Mode**. Both hands are tracked independently with distinct glowing HUD colors (Hand 1 in Cyan, Hand 2 in Magenta) and an active sci-fi energy span beam connecting them. You can perform high-level spatial gestures like zoom, rotate, screenshot framing, clap pause, and window snapping!

---

## 🖐️ Single-Hand Gestures

### 1. Mouse Movement (Open Palm or Index-Finger Air Pointer)
- **Hand Pose**: Either:
  - **Index-Finger Air Pointer**: Extend your **Index Finger** to point and aim (like a laser pointer or Wiimote).
  - **Open Palm**: Hold all 5 fingers relaxed and extended.
- **Action**: Moves the PC cursor with momentum, acceleration, and $1€$ OneEuro jitter filtering.
- **How to do it**: Point with your index finger or hold your open hand facing the camera and move smoothly in any direction. The cursor follows your Index MCP joint stably without jitter.

---

### 2. Left Click (Index Pinch)
- **Hand Pose**: Pinch your **Thumb Tip** and **Index Tip** together.
- **Action**: Triggers a standard Left Mouse Click (`pyautogui.click()`).
- **How to do it**: Quickly touch thumb and index finger together. The HUD reticle will contract and turn **Red**, and you'll hear a crisp audio click. Clicks are top priority and trigger instantly without collision.

---

### 3. Double Click (Double Pinch)
- **Hand Pose**: Pinch **Thumb + Index** twice within 0.38 seconds.
- **Action**: Triggers Double Click (`pyautogui.doubleClick()`).
- **How to do it**: Tap thumb and index together twice rapidly to open folders, launch desktop icons, or select words.

---

### 4. 3D Air Tap (Push-to-Click)
- **Hand Pose**: Extend your **Index Finger** and push it **forward toward the camera** along the Z-axis.
- **Action**: Contactless 3D click without pinching (Apple Vision Pro style).
- **How to do it**: Point with your index finger and give a deliberate forward jab toward the webcam.

---

### 5. Right Click (Middle Pinch)
- **Hand Pose**: Pinch your **Thumb Tip** and **Middle Tip** together.
- **Action**: Triggers Right Click (Context Menu).
- **How to do it**: Touch the tip of your thumb to your middle finger while keeping index finger relaxed.

---

### 6. Middle Click / New Tab (Ring Pinch)
- **Hand Pose**: Pinch your **Thumb Tip** and **Ring Tip** together.
- **Action**: Triggers Middle Mouse Button (`pyautogui.middleClick()`).
- **How to do it**: Pinch thumb and ring finger to open browser links in new background tabs or close tabs.

---

### 7. Drag & Drop (Closed Fist Toggle)
- **Hand Pose**: Make a tight **Closed Fist** (all fingers curled into palm).
- **Action**: Toggles Mouse Down / Drag Lock (`mouseDown()` $\leftrightarrow$ `mouseUp()`).
- **How to do it**:
  1. Position cursor over an item or window title bar.
  2. Make a fist: The HUD glows **Neon Green** and displays `"✊ DRAG LOCKED"`.
  3. Move your hand to drag the window, select text, or move files.
  4. Make a fist again to release (`"✋ DRAG RELEASED"`).

---

### 8. Vertical Scroll (Peace Sign)
- **Hand Pose**: **Peace / Victory Sign ($V$)** (Index and Middle fingers UP, Ring and Pinky curled down).
- **Action**: Scrolls pages up or down proportionally.
- **How to do it**: Show the $V$ sign vertically:
  - Move hand **UP** to scroll up.
  - Move hand **DOWN** to scroll down.

---

### 9. Horizontal Scroll (Horizontal Peace Sign)
- **Hand Pose**: Tilt your **Peace Sign sideways** ($> 45^\circ$ angle).
- **Action**: Horizontal scroll (`hscroll`) for video timelines, Excel sheets, and wide canvases.
- **How to do it**: Tilt the $V$ horizontally and move hand left/right.

---

### 10. Volume Up (Thumbs Up 👍)
- **Hand Pose**: Extend your **Thumb UP** while curling Index, Middle, Ring, and Pinky into a fist.
- **Action**: Increments Windows Master Volume (`volumeup`).
- **How to do it**: Hold a clear thumbs-up. The HUD shows a golden notification `"🔊 VOLUME UP"` and ramps up volume smoothly.

---

### 11. Volume Down (Thumbs Down 👎)
- **Hand Pose**: Point your **Thumb DOWN** while curling Index, Middle, Ring, and Pinky into a fist.
- **Action**: Decrements Windows Master Volume (`volumedown`).
- **How to do it**: Point thumb downward to lower sound smoothly.

---

### 12. Mute / Unmute (Pinky Promise 🤙)
- **Hand Pose**: Extend only your **Pinky Finger UP**, with all other fingers curled down.
- **Action**: Toggles Windows Audio Mute (`volumemute`).
- **How to do it**: Raise your pinky finger like a pinky promise. Instant silence / unmute.

---

### 13. Play / Pause Media (Three Fingers Up 🖐️)
- **Hand Pose**: Extend **Index, Middle, and Ring Fingers UP**, with Pinky and Thumb curled.
- **Action**: Media Play / Pause (`playpause`) for Spotify, YouTube, VLC, Netflix.
- **How to do it**: Show 3 fingers upright facing the camera. Keeps Left Click completely independent and conflict-free!

---

### 14. Track Switch Next / Prev (Gun Gesture 👉 / 👈)
- **Hand Pose**: Gun pose with **Thumb pointing UP** (the hammer) and **Index Finger extended horizontally** (the barrel).
- **Action**:
  - Pointing **RIGHT 👉**: Next Track (`nexttrack`).
  - Pointing **LEFT 👈**: Previous Track (`prevtrack`).
- **How to do it**: Form a finger gun pointing right or left with your thumb cocked up. (Normal pointing without thumb up simply moves the cursor smoothly).

---

### 15. Show Desktop (Spider-Man / Rock-On 🤟)
- **Hand Pose**: Extend **Thumb, Index, and Pinky**, while curling **Middle and Ring** fingers down.
- **Action**: Minimizes all windows to reveal desktop (`Win + D`).
- **How to do it**: Make the Spider-Man web-shooter sign. Do it again to restore all windows.

---

### 16. App Switcher / Alt-Tab (Four Fingers ✋)
- **Hand Pose**: Extend **Index, Middle, Ring, and Pinky** UP, while tucking **Thumb** across palm.
- **Action**: Triggers Windows Task Switcher (`Alt + Tab`).
- **How to do it**: Show four fingers (tucking your thumb inside).

---

## 👐 Two-Hand Bimanual Gestures

*When both hands enter camera view, the HUD connects them with a dynamic neon beam and enters Bimanual Mode.*

---

### 1. Two-Hand Zoom In / Out
- **Hand Pose**: Both hands visible with open palms or index pinches facing the camera.
- **Action**:
  - **Spread hands apart outward** $\rightarrow$ **Zoom In** (`Ctrl + +`).
  - **Bring hands closer inward** $\rightarrow$ **Zoom Out** (`Ctrl + -`).
- **How to do it**: Just like zooming on an iPad or touch screen! Move hands closer together or pull them apart in the air. Perfect for Google Maps, browser pages, and image viewers.

---

### 2. Two-Hand Rotate CW / CCW
- **Hand Pose**: Hold both hands up at shoulder width.
- **Action**:
  - Rotate hands clockwise (Right hand down, Left hand up) $\rightarrow$ **Rotate CW** (`Ctrl + Alt + Right`).
  - Rotate hands counter-clockwise (Right hand up, Left hand down) $\rightarrow$ **Rotate CCW** (`Ctrl + Alt + Left`).
- **How to do it**: Rotate an imaginary steering wheel with both hands.

---

### 3. Screenshot Snipping Tool (L-Frame Box 📐)
- **Hand Pose**:
  - **Left Hand**: Thumb pointing right, Index finger pointing UP (Forms an "L").
  - **Right Hand**: Thumb pointing left, Index finger pointing UP (Forms an inverted "L").
- **Action**: Automatically triggers Windows Screen Snip (`Win + Shift + S`).
- **How to do it**: Form a rectangular camera viewfinder framing an area with your two hands. The HUD overlays illuminated cyan corner brackets and captures the snip!

---

### 4. Two-Hand Clap (Freeze / Emergency Pause 👏)
- **Hand Pose**: Bring both hands together quickly in a clap (distance between wrists drops below threshold).
- **Action**: Instantly freezes/pauses the entire tracking system (`[ SYSTEM PAUSED ]`).
- **How to do it**: Clap your hands once in front of the webcam. Clap again to resume control.

---

### 5. Window Maximize / Minimize
- **Hand Pose**: Both hands open facing camera.
- **Action**:
  - Push both hands outward rapidly $\rightarrow$ **Maximize Active Window** (`Win + Up`).
  - Pull both hands inward rapidly $\rightarrow$ **Minimize Active Window** (`Win + Down`).
- **How to do it**: Make an expansive outward gesture to maximize, or a contracting inward gesture to minimize.

---

### 6. Dual Volume Slider
- **Hand Pose**:
  - **Left Hand**: Make a **Closed Fist** (acts as the anchor dial).
  - **Right Hand**: Extend **Index Finger**.
- **Action**: Moving the right index finger **UP** increases volume; moving it **DOWN** decreases volume.
- **How to do it**: Hold left fist still, and slide your right index up and down like a mixing board fader.

---

---

## 🚀 Advanced Next-Gen Modules

### 1. Interactive Spatial Node Constellation (Point 1)
- **What it is**: A full-screen cyberpunk interface rendering an interconnected network of 3D/2D interactive nodes (Plexus / Neural constellation) powered by physics springs and real-time hand tracking.
- **How to launch**:
  - Press **`N`** inside the app, or open your browser at **`http://127.0.0.1:8765/`**.
- **Hand Gesture Controls inside Node Constellation**:
  - **Hover**: Move hand across the screen to hover over nodes; connection lines pulse with energy and an inspection HUD card pops out with telemetry.
  - **Pinch to Grab / Drag**: Pinch (Thumb+Index) over any node to grab it in space and drag it around; connected springs stretch and react dynamically.
  - **2-Hand Zoom / Expand**: Spread two hands apart to expand the constellation into a giant galaxy; bring hands together to collapse it into a tight core.
  - **2-Hand Rotate**: Rotate your two hands to orbit the node graph in 3D.
  - **Fist Shockwave**: Make a fist to trigger a shockwave ripple that disperses nodes outward!

---

### 2. $1 Unistroke Custom Gesture Macro Recorder (Point 4)
- **What it is**: An AI-based spatio-temporal gesture matcher. Trace letters, shapes, or symbols in thin air to trigger OS commands!
- **Pre-loaded Air Gestures**:
  - Draw **`"C"`** in the air $\rightarrow$ Launches **Google Chrome**
  - Draw **`"S"`** in the air $\rightarrow$ Launches **Spotify**
  - Draw **`"O"` (Circle)** in the air $\rightarrow$ Refreshes Webpage (`F5`)
  - Draw **`"Z"`** in the air $\rightarrow$ Triggers Undo (`Ctrl + Z`)
  - Draw **`"^"` (Up Arrow)** in the air $\rightarrow$ Triggers Windows Task View (`Win + Tab`)
- **How to record your own custom gesture**:
  1. Press **`R`**: HUD displays `"🔴 REC MACRO: Trace gesture in air..."`
  2. Draw your custom shape in mid-air.
  3. Press **`R`** again: System normalizes the stroke, saves it to `custom_macros.json`, and confirms with `"✅ SAVED"`.

---

### 3. Virtual Camera for Zoom, Teams & Meet (Point 5)
- **What it is**: Streams your live mirrored webcam with futuristic holographic skeletal overlays, tracking reticles, and gesture badges into a **Virtual Camera**.
- **How to use**:
  - Press **`V`** to toggle Virtual Camera streaming on/off.
  - In **Zoom, Microsoft Teams, Google Meet, Discord, or OBS**, open Video Settings and choose **"OBS Virtual Camera"** or **"Project Air Virtual Camera"**.
  - Your attendees will see you with real-time *Iron Man / Minority Report* holographic hand tracking overlays!

---

### 4. Context-Aware Application Profiles ("Air StreamDeck" - Point 2)
- Automatically senses the active foreground window and customizes your gesture controls:
  - **🎵 Media Mode (Spotify, YouTube, VLC)**: Optimized for volume adjustments, play/pause, and track skipping.
  - **📽️ Presentation Mode (PowerPoint, PDF Slides)**: Index finger becomes a **Virtual Laser Pointer**; flick gestures navigate slides forward/back; fist blacks out the screen.
  - **🌐 Browser Mode (Chrome, Edge, IDE)**: Pinch zooms web pages; gestures cycle browser tabs (`Ctrl + Tab`).

---

### 5. Virtual Air Canvas & Mid-Air Whiteboard (Point 3)
- **What it is**: Draw, sketch, and annotate in thin air directly over your desktop or during video calls.
- **How to use**:
  - Press **`C`** to toggle Air Canvas ON/OFF.
  - Pinch **Thumb + Index** to lay down glowing neon paint strokes with your index finger.
  - Pinch **Thumb + Middle** to cycle colors (Cyan, Green, Pink, Gold, White).
  - Press **`E`** (or shake your hand) to wipe the canvas clean.

---

## ⌨️ Master Keyboard Shortcuts

| Key | Function |
| :---: | :--- |
| **`Q`** | Quit application safely & stop all servers |
| **`F`** | Toggle **Fast Mode** ($1.6\times$ cursor speed boost) |
| **`P`** | Toggle **Pause / Resume** |
| **`N`** | Launch **Spatial Node Matrix** in browser (`http://127.0.0.1:8765/`) |
| **`C`** | Toggle **Air Canvas** (Mid-Air Whiteboard) |
| **`E`** | **Erase / Wipe** Air Canvas Clean |
| **`V`** | Toggle **Virtual Camera** (Stream to Zoom / Teams / Meet) |
| **`R`** | Toggle **Macro REC Mode** (Record custom gestures in mid-air) |

### Tuning Parameters
You can adjust sensitivity, thresholds, and cooldowns anytime in [gesture_v3/config.py](file:///d:/HandGes%20-%20CV/gesture_v3/config.py):
- `BASE_SENSITIVITY`: Cursor speed multiplier (default: `4.5`)
- `ACCELERATION_FACTOR`: Non-linear momentum gain (default: `16.0`)
- `PINCH_THRESHOLD_NORM`: Pinch sensitivity (default: `0.07`)
- `ENABLE_AUDIO_FEEDBACK`: Enable/disable sound clicks (default: `True`)
- `ENABLE_WEB_BRIDGE`: Enable/disable local Node Matrix server (default: `True`)
- `ENABLE_CLAHE_ENHANCER`: Enable/disable low-light adaptive contrast (default: `True`)
