import cv2
import time
import math
import threading
import webbrowser
import pyautogui
from gesture_v3 import config
from gesture_v3.perception.tracker import HandTracker
from gesture_v3.perception.smoothing import OneEuroFilter
from gesture_v3.intent.classifier import GestureClassifier
from gesture_v3.control.mouse_physics import PhysicsCursor
from gesture_v3.ui.hud import CinematicHUD
from gesture_v3.intent.macro_engine import Dollar1Recognizer
from gesture_v3.ui.virtual_cam import VirtualCamStreamer
from gesture_v3.intent.app_profiles import AppProfileManager
from gesture_v3.control.air_canvas import AirCanvas
from gesture_v3.core.server import SpatialWebServer

try:
    import winsound
except ImportError:
    winsound = None

pyautogui.FAILSAFE = False

def play_audio_feedback(freq=1800, dur=25):
    """Play subtle non-blocking audio feedback click on Windows"""
    if config.ENABLE_AUDIO_FEEDBACK and winsound:
        threading.Thread(target=winsound.Beep, args=(freq, dur), daemon=True).start()

class SystemController:
    """
    Main application loop. Orchestrates camera input, 1-hand & 2-hand gesture recognition,
    physics cursor control, multimedia commands, sci-fi HUD rendering, and advanced spatial modules:
    - $1 Unistroke Macro Engine
    - Virtual Camera (Zoom/Teams)
    - Context-Aware App Profiles (Spotify/PPT/Browser)
    - Mid-Air Whiteboard (Air Canvas)
    - Web Spatial Bridge (Interactive Node Constellation)
    """
    CAMERA_WIDTH = getattr(config, 'CAMERA_WIDTH', 640)
    CAMERA_HEIGHT = getattr(config, 'CAMERA_HEIGHT', 480)
    CAMERA_INDEX = 0
    INITIAL_SMOOTHING_POSITION = [0.5, 0.5]

    def __init__(self):
        self.running = True
        self.is_paused = False
        self.smoothed_fps = 30.0
        self.cap = cv2.VideoCapture(self.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)
        
        self.tracker = HandTracker()
        self.start_time = time.time()
        
        # State tracking
        self.prev_hand_x = None
        self.prev_hand_y = None
        self.last_scroll_y = None
        self.last_scroll_x = None
        self.drag_active = False

        # Advanced Next-Gen Modules
        self.macro_engine = Dollar1Recognizer()
        self.virtual_cam = VirtualCamStreamer(self.CAMERA_WIDTH, self.CAMERA_HEIGHT, config.TARGET_FPS)
        self.profile_mgr = AppProfileManager()
        self.air_canvas = AirCanvas(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        self.web_server = SpatialWebServer()
        if getattr(config, 'ENABLE_WEB_BRIDGE', True):
            self.web_server.start()

        # Macro stroke recording
        self.macro_stroke = []
        self.is_recording_custom_macro = False
        self.custom_macro_pts = []
        self.last_macro_eval_time = 0

        # Cooldown timestamps
        self.last_click_time = 0
        self.last_right_click_time = 0
        self.last_middle_click_time = 0
        self.last_toggle_time = 0
        self.last_media_time = 0
        self.last_volume_time = 0
        self.last_track_time = 0
        self.last_hotkey_time = 0
        self.last_zoom_time = 0
        self.last_rotate_time = 0
        self.last_window_time = 0
        self.last_clap_time = 0

    def run(self):
        """Main application loop"""
        print(f"[{config.APP_NAME}] Initialized. Press 'Q' to quit | 'P' to pause.")
        
        smoother = OneEuroFilter(
            time.time(), 
            self.INITIAL_SMOOTHING_POSITION,
            min_cutoff=config.ONE_EURO_MIN_CUTOFF, 
            beta=config.ONE_EURO_BETA
        )
        classifier = GestureClassifier()
        cursor = PhysicsCursor()
        hud = CinematicHUD()
        
        last_time = time.time()

        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            success, img = self.cap.read()
            if not success:
                continue

            # Mirror image for intuitive interaction
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_timestamp_ms = (current_time - self.start_time) * 1000
            
            # Calculate smoothed FPS (adaptive scaling, never pauses execution)
            inst_fps = 1.0 / dt if dt > 0 else 30.0
            self.smoothed_fps = 0.9 * self.smoothed_fps + 0.1 * inst_fps

            # Process hand detection (up to 2 hands)
            detection_result = self.tracker.process(img_rgb, frame_timestamp_ms)
            
            if detection_result and detection_result.hand_landmarks:
                self._process_detection(
                    detection_result, img, classifier, smoother, cursor, hud, current_time, dt
                )
            else:
                self._process_hand_lost(cursor, hud, img)
            
            # FPS counter display
            cv2.putText(img, f"{config.APP_NAME} | FPS: {int(self.smoothed_fps)}", 
                       (20, 32), cv2.FONT_HERSHEY_PLAIN, 1.1, (200, 255, 200), 1, cv2.LINE_AA)
            cv2.imshow(config.APP_NAME, img)

            # Keyboard shortcuts
            self._handle_input(cursor, hud)

        self.cap.release()
        cv2.destroyAllWindows()

    def _process_detection(self, detection_result, img, classifier, smoother, cursor, hud, current_time, dt):
        """Route to 1-hand or 2-hand processing based on visible hands"""
        hands = detection_result.hand_landmarks
        hand_count = len(hands)

        if self.is_paused:
            hud.draw(img, hands, "PAUSED", 1.0, "PAUSED", is_paused=True)
            return

        dual_state = "NONE"
        if hand_count >= 2:
            # Sort hands horizontally: left-side hand and right-side hand on screen
            h1, h2 = hands[0], hands[1]
            hand_left, hand_right = (h1, h2) if h1[0].x < h2[0].x else (h2, h1)
            
            dual_state, dual_meta = classifier.process_dual(hand_left, hand_right)
            
            # Execute bimanual action if detected
            bimanual_handled = self._execute_dual_gesture(dual_state, hud, current_time)
            
            if bimanual_handled:
                # Hands are performing a dual gesture (e.g. Zoom, Rotate, Frame)
                hud.draw(img, [hand_left, hand_right], "BIMANUAL", 1.0, dual_state, is_paused=self.is_paused)
                return

        # Single Hand / Primary Hand Processing (Dominant hand navigation)
        primary_hand = hands[0]
        # Use Index MCP (joint 5) for cursor tracking stability
        raw_point = primary_hand[5]
        norm_x, norm_y = raw_point.x, raw_point.y
        
        filtered_pos = smoother(current_time, [norm_x, norm_y])
        curr_x, curr_y = filtered_pos[0], filtered_pos[1]
        
        if self.prev_hand_x is not None:
            delta_x = curr_x - self.prev_hand_x
            delta_y = curr_y - self.prev_hand_y
        else:
            delta_x = delta_y = 0.0
        
        self.prev_hand_x = curr_x
        self.prev_hand_y = curr_y
        
        single_state, meta = classifier.process_single(primary_hand)
        
        # 1. Update Context-Aware Application Profile (Spotify / PPT / Browser)
        current_profile, active_title = self.profile_mgr.update()

        # 2. Check if Profile wants custom handling
        profile_handled = self.profile_mgr.handle_profile_action(current_profile, single_state, hud, current_time)

        # 3. If not handled by profile, execute standard single-hand action
        if not profile_handled:
            self._execute_single_gesture(single_state, delta_x, delta_y, dt, cursor, hud, current_time, norm_x, norm_y)

        # 4. Air Canvas Spatial Drawing (if active)
        if self.air_canvas.is_active:
            self.air_canvas.process(primary_hand, single_state, hud)

        # 5. Macro Stroke Tracking & Recognition
        index_tip = primary_hand[8]
        pt = (int(index_tip.x * self.CAMERA_WIDTH), int(index_tip.y * self.CAMERA_HEIGHT))
        if self.is_recording_custom_macro:
            self.custom_macro_pts.append(pt)
        else:
            if single_state in ["MOVE", "CLICK_LEFT"]:
                self.macro_stroke.append(pt)
            else:
                if len(self.macro_stroke) >= 12 and (current_time - self.last_macro_eval_time > 0.6):
                    matched, score, action, label = self.macro_engine.recognize(self.macro_stroke)
                    if matched and action:
                        self.macro_engine.execute_action(action)
                        hud.trigger_notification(f"✨ MACRO: {label} ({int(score*100)}%)", (255, 0, 180), duration=1.2)
                        play_audio_feedback(2200, 40)
                    self.macro_stroke.clear()
                    self.last_macro_eval_time = current_time

            if len(self.macro_stroke) > 60:
                self.macro_stroke = self.macro_stroke[-30:]

        # 6. Stream real-time data to Spatial Bridge Web Server (Node Constellation)
        if self.web_server:
            fps_val = int(1.0 / dt) if dt > 0 else 60
            self.web_server.update_state(
                hands=[[{"x": lm.x, "y": lm.y, "z": lm.z} for lm in h] for h in hands],
                state=single_state,
                dual_state=dual_state,
                cursor={"x": norm_x, "y": norm_y},
                is_pinching=(single_state in ["CLICK_LEFT", "DRAG_ACTIVE"]),
                fps=fps_val,
                profile=current_profile,
                active_window=active_title
            )

        display_state = single_state
        if cursor.fast_mode and single_state == "MOVE":
            display_state = "FAST_MOVE"
        
        hud.draw(img, hands, display_state, 1.0, dual_state, is_paused=self.is_paused,
                 profile=current_profile, vcam_active=self.virtual_cam.is_active)

        # 7. Blend Air Canvas strokes onto frame
        img = self.air_canvas.blend(img)

        # 8. Send frame to Virtual Camera (Zoom / Teams / OBS)
        self.virtual_cam.send(img)

    def _execute_dual_gesture(self, dual_state, hud, current_time):
        """Execute actions for bimanual 2-hand gestures. Returns True if handled."""
        if dual_state == "CLAP":
            if (current_time - self.last_clap_time) > config.CLAP_COOLDOWN:
                self.is_paused = not self.is_paused
                self.last_clap_time = current_time
                msg = "⏸️ SYSTEM PAUSED" if self.is_paused else "▶️ SYSTEM RESUMED"
                hud.trigger_notification(msg, (0, 0, 255) if self.is_paused else (0, 255, 0))
                play_audio_feedback(1200, 60)
            return True

        if dual_state == "FRAME_CAPTURE":
            if (current_time - self.last_hotkey_time) > config.HOTKEY_COOLDOWN:
                pyautogui.hotkey('win', 'shift', 's')
                self.last_hotkey_time = current_time
                hud.trigger_notification("📸 SCREENSHOT SNIP", (0, 255, 255))
                play_audio_feedback(2400, 50)
            return True

        if dual_state == "TWO_HAND_ZOOM_IN":
            if (current_time - self.last_zoom_time) > config.ZOOM_COOLDOWN:
                pyautogui.hotkey('ctrl', '+')
                self.last_zoom_time = current_time
                hud.trigger_notification("🔍 ZOOM IN", config.COLOR_BIMANUAL, duration=0.4)
                play_audio_feedback(1900, 15)
            return True

        if dual_state == "TWO_HAND_ZOOM_OUT":
            if (current_time - self.last_zoom_time) > config.ZOOM_COOLDOWN:
                pyautogui.hotkey('ctrl', '-')
                self.last_zoom_time = current_time
                hud.trigger_notification("🔍 ZOOM OUT", config.COLOR_BIMANUAL, duration=0.4)
                play_audio_feedback(1600, 15)
            return True

        if dual_state == "TWO_HAND_ROTATE_CW":
            if (current_time - self.last_rotate_time) > config.ROTATE_COOLDOWN:
                pyautogui.hotkey('ctrl', 'alt', 'right')
                self.last_rotate_time = current_time
                hud.trigger_notification("🔄 ROTATE CW", config.COLOR_BIMANUAL, duration=0.5)
                play_audio_feedback(1700, 20)
            return True

        if dual_state == "TWO_HAND_ROTATE_CCW":
            if (current_time - self.last_rotate_time) > config.ROTATE_COOLDOWN:
                pyautogui.hotkey('ctrl', 'alt', 'left')
                self.last_rotate_time = current_time
                hud.trigger_notification("🔄 ROTATE CCW", config.COLOR_BIMANUAL, duration=0.5)
                play_audio_feedback(1700, 20)
            return True

        if dual_state == "WINDOW_MAX":
            if (current_time - self.last_window_time) > config.WINDOW_SNAP_COOLDOWN:
                pyautogui.hotkey('win', 'up')
                self.last_window_time = current_time
                hud.trigger_notification("🗖 MAXIMIZE WINDOW", (255, 200, 0))
                play_audio_feedback(2000, 40)
            return True

        if dual_state == "WINDOW_MIN":
            if (current_time - self.last_window_time) > config.WINDOW_SNAP_COOLDOWN:
                pyautogui.hotkey('win', 'down')
                self.last_window_time = current_time
                hud.trigger_notification("🗕 MINIMIZE WINDOW", (255, 200, 0))
                play_audio_feedback(1500, 40)
            return True

        if dual_state == "DUAL_VOL_UP":
            if (current_time - self.last_volume_time) > config.VOLUME_HOLD_COOLDOWN:
                pyautogui.press('volumeup')
                self.last_volume_time = current_time
                hud.trigger_notification("🔊 VOLUME UP", config.COLOR_MEDIA, duration=0.3)
                play_audio_feedback(1800, 15)
            return True

        if dual_state == "DUAL_VOL_DOWN":
            if (current_time - self.last_volume_time) > config.VOLUME_HOLD_COOLDOWN:
                pyautogui.press('volumedown')
                self.last_volume_time = current_time
                hud.trigger_notification("🔉 VOLUME DOWN", config.COLOR_MEDIA, duration=0.3)
                play_audio_feedback(1400, 15)
            return True

        return False

    def _execute_single_gesture(self, state, delta_x, delta_y, dt, cursor, hud, current_time, norm_x, norm_y):
        """Execute single-hand mouse, multimedia, and navigation commands"""
        # Reset scroll tracking when outside scroll modes to prevent page jumps
        if state != "SCROLL_V":
            self.last_scroll_y = None
        if state != "SCROLL_H":
            self.last_scroll_x = None

        # Fist toggles drag mode
        if state == "FIST":
            self._handle_drag_toggle(current_time, hud)
        
        # Cursor movement in Move or Drag states
        if self.drag_active:
            if state in ["MOVE", "IDLE", "FIST"]:
                cursor.update_relative(delta_x, delta_y, dt)
            return
        
        if state == "MOVE":
            cursor.update_relative(delta_x, delta_y, dt)

        elif state == "CLICK_LEFT":
            if (current_time - self.last_click_time) > config.CLICK_COOLDOWN:
                # Double click detection
                if (current_time - self.last_click_time) < config.DOUBLE_CLICK_INTERVAL:
                    pyautogui.doubleClick()
                    hud.trigger_notification("🖱️ DOUBLE CLICK", (0, 0, 255))
                    play_audio_feedback(2200, 40)
                    self.last_click_time = 0
                else:
                    pyautogui.click()
                    hud.trigger_notification("🖱️ LEFT CLICK", (0, 0, 255))
                    play_audio_feedback(1800, 25)
                    self.last_click_time = current_time

        elif state == "AIR_TAP":
            pyautogui.click()
            hud.trigger_notification("⚡ 3D AIR TAP CLICK", (0, 140, 255))
            play_audio_feedback(2000, 30)

        elif state == "CLICK_RIGHT":
            if (current_time - self.last_right_click_time) > config.CLICK_COOLDOWN:
                pyautogui.rightClick()
                self.last_right_click_time = current_time
                hud.trigger_notification("🖱️ RIGHT CLICK", config.COLOR_RIGHT_CLICK)
                play_audio_feedback(1500, 30)

        elif state == "CLICK_MIDDLE":
            if (current_time - self.last_middle_click_time) > config.CLICK_COOLDOWN:
                pyautogui.middleClick()
                self.last_middle_click_time = current_time
                hud.trigger_notification("🖱️ MIDDLE CLICK (TAB)", config.COLOR_MIDDLE_CLICK)
                play_audio_feedback(1600, 30)

        elif state == "SCROLL_V":
            self._handle_scroll_vertical(norm_y)

        elif state == "SCROLL_H":
            self._handle_scroll_horizontal(norm_x)

        elif state == "VOL_UP":
            if (current_time - self.last_volume_time) > config.VOLUME_HOLD_COOLDOWN:
                pyautogui.press('volumeup')
                self.last_volume_time = current_time
                hud.trigger_notification("🔊 VOLUME UP", config.COLOR_MEDIA, duration=0.3)
                play_audio_feedback(1900, 15)

        elif state == "VOL_DOWN":
            if (current_time - self.last_volume_time) > config.VOLUME_HOLD_COOLDOWN:
                pyautogui.press('volumedown')
                self.last_volume_time = current_time
                hud.trigger_notification("🔉 VOLUME DOWN", config.COLOR_MEDIA, duration=0.3)
                play_audio_feedback(1400, 15)

        elif state == "MUTE":
            if (current_time - self.last_media_time) > config.MEDIA_ACTION_COOLDOWN:
                pyautogui.press('volumemute')
                self.last_media_time = current_time
                hud.trigger_notification("🔇 MUTE TOGGLE", (0, 165, 255))
                play_audio_feedback(1300, 40)

        elif state == "PLAY_PAUSE":
            if (current_time - self.last_media_time) > config.MEDIA_ACTION_COOLDOWN:
                pyautogui.press('playpause')
                self.last_media_time = current_time
                hud.trigger_notification("⏯️ PLAY / PAUSE", (0, 255, 100))
                play_audio_feedback(2100, 35)

        elif state == "NEXT_TRACK":
            if (current_time - self.last_track_time) > config.TRACK_SWITCH_COOLDOWN:
                pyautogui.press('nexttrack')
                self.last_track_time = current_time
                hud.trigger_notification("⏭️ NEXT TRACK", (255, 200, 0))
                play_audio_feedback(2000, 30)

        elif state == "PREV_TRACK":
            if (current_time - self.last_track_time) > config.TRACK_SWITCH_COOLDOWN:
                pyautogui.press('prevtrack')
                self.last_track_time = current_time
                hud.trigger_notification("⏮️ PREVIOUS TRACK", (255, 200, 0))
                play_audio_feedback(1700, 30)

        elif state == "SHOW_DESKTOP":
            if (current_time - self.last_hotkey_time) > config.HOTKEY_COOLDOWN:
                pyautogui.hotkey('win', 'd')
                self.last_hotkey_time = current_time
                hud.trigger_notification("🖥️ SHOW DESKTOP", (255, 0, 180))
                play_audio_feedback(2200, 45)

        elif state == "ALT_TAB":
            if (current_time - self.last_hotkey_time) > config.HOTKEY_COOLDOWN:
                pyautogui.hotkey('alt', 'tab')
                self.last_hotkey_time = current_time
                hud.trigger_notification("📑 SWITCH APP (ALT+TAB)", (255, 165, 0))
                play_audio_feedback(1800, 40)

    def _handle_drag_toggle(self, current_time, hud):
        """Toggle mouse drag latch"""
        if (current_time - self.last_toggle_time) > config.DRAG_TOGGLE_COOLDOWN:
            self.drag_active = not self.drag_active
            self.last_toggle_time = current_time
            
            if self.drag_active:
                pyautogui.mouseDown()
                hud.trigger_notification("✊ DRAG LOCKED", (0, 255, 0))
                play_audio_feedback(1200, 40)
            else:
                pyautogui.mouseUp()
                hud.trigger_notification("✋ DRAG RELEASED", (0, 255, 255))
                play_audio_feedback(1600, 30)

    def _handle_scroll_vertical(self, norm_y):
        """Scroll vertical pages proportionally"""
        if self.last_scroll_y is not None:
            dy = norm_y - self.last_scroll_y
            if abs(dy) > config.SCROLL_DEADZONE:
                scroll_amount = int(-dy * config.SCROLL_SPEED * 100)
                pyautogui.scroll(scroll_amount)
        self.last_scroll_y = norm_y

    def _handle_scroll_horizontal(self, norm_x):
        """Scroll horizontal pages / timelines proportionally"""
        if self.last_scroll_x is not None:
            dx = norm_x - self.last_scroll_x
            if abs(dx) > config.SCROLL_DEADZONE:
                scroll_amount = int(dx * config.SCROLL_SPEED * 80)
                pyautogui.hscroll(scroll_amount)
        self.last_scroll_x = norm_x

    def _process_hand_lost(self, cursor, hud, img):
        """Cleanup states when hands exit camera view"""
        if self.drag_active:
            pyautogui.mouseUp()
            self.drag_active = False
        
        self.prev_hand_x = None
        self.prev_hand_y = None
        self.last_scroll_y = None
        self.last_scroll_x = None
        self.macro_stroke.clear()

        # Update Web Bridge to idle
        if self.web_server:
            self.web_server.update_state(
                hands=[],
                state="IDLE",
                is_pinching=False
            )
        
        hud.draw(img, None, "IDLE", 0.0, is_paused=self.is_paused, vcam_active=self.virtual_cam.is_active)
        img = self.air_canvas.blend(img)
        self.virtual_cam.send(img)

    def _display_safety_message(self, img, message):
        """Display safety warning overlay"""
        text = f"SAFETY PAUSE: {message}"
        cv2.putText(img, text, 
                   (config.WINDOW_WIDTH // 2 - 200, config.WINDOW_HEIGHT // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow(config.APP_NAME, img)
        cv2.waitKey(1)

    def _handle_input(self, cursor, hud):
        """Handle keyboard triggers for all core and next-gen features"""
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.running = False
            self.virtual_cam.stop()
            if self.web_server:
                self.web_server.stop()
        elif key == ord('f'):
            cursor.set_fast_mode(not cursor.fast_mode)
            status = "ON" if cursor.fast_mode else "OFF"
            hud.trigger_notification(f"⚡ FAST MODE: {status}", (0, 255, 255))
            play_audio_feedback(2200 if cursor.fast_mode else 1400, 30)
        elif key == ord('p'):
            self.is_paused = not self.is_paused
            msg = "⏸️ SYSTEM PAUSED" if self.is_paused else "▶️ SYSTEM RESUMED"
            hud.trigger_notification(msg, (0, 0, 255) if self.is_paused else (0, 255, 0))
            play_audio_feedback(1200, 50)
        elif key == ord('c'):
            is_on = self.air_canvas.toggle()
            hud.trigger_notification(f"🎨 AIR CANVAS: {'ON' if is_on else 'OFF'}", (255, 0, 255))
            play_audio_feedback(2000 if is_on else 1500, 30)
        elif key == ord('e'):
            self.air_canvas.clear()
            hud.trigger_notification("🧹 CANVAS WIPED CLEAN", (200, 200, 200))
            play_audio_feedback(1400, 25)
        elif key == ord('v'):
            success, msg = self.virtual_cam.toggle()
            col = (0, 255, 255) if success else (0, 0, 255)
            hud.trigger_notification(f"🎥 {msg}", col, duration=1.8)
            play_audio_feedback(2400 if success else 1000, 40)
        elif key == ord('r'):
            self.is_recording_custom_macro = not self.is_recording_custom_macro
            if self.is_recording_custom_macro:
                self.custom_macro_pts = []
                hud.trigger_notification("🔴 REC MACRO: Trace gesture in air...", (0, 0, 255), duration=2.5)
                play_audio_feedback(2000, 60)
            else:
                if len(self.custom_macro_pts) >= 12:
                    macro_id = f"MACRO_{int(time.time()) % 1000}"
                    self.macro_engine.save_custom_template(macro_id, self.custom_macro_pts, "hotkey:win,d", label=macro_id)
                    hud.trigger_notification(f"✅ SAVED: {macro_id} (Win+D)", (0, 255, 0), duration=2.5)
                    play_audio_feedback(2600, 80)
                else:
                    hud.trigger_notification("❌ STROKE TOO SHORT (Not saved)", (0, 0, 255), duration=1.5)
        elif key == ord('n'):
            webbrowser.open(f"http://127.0.0.1:{config.WEB_SERVER_PORT}")
            hud.trigger_notification("⟁ OPENING SPATIAL NODE MATRIX...", (0, 240, 255), duration=1.5)
            play_audio_feedback(2200, 40)
