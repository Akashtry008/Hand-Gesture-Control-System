
import cv2
import time
import pyautogui
from gesture_v3 import config
from gesture_v3.perception.tracker import HandTracker
from gesture_v3.perception.smoothing import OneEuroFilter
from gesture_v3.intent.classifier import GestureClassifier
from gesture_v3.control.mouse_physics import PhysicsCursor
from gesture_v3.ui.hud import CinematicHUD

pyautogui.FAILSAFE = False

class SystemController:
    """
    Main application loop. Orchestrates camera input through gesture recognition to mouse control.
    """
    # Camera settings
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_INDEX = 0
    
    # Smoothing settings for hand tracking
    INITIAL_SMOOTHING_POSITION = [0.5, 0.5]
    
    def __init__(self):
        self.running = True
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
        self.drag_active = False
        self.last_toggle_time = 0
        self.last_click_time = 0
        
    def run(self):
        """Main application loop"""
        print(f"[{config.APP_NAME}] Initialized. Press 'Q' to quit.")
        
        # Initialize subsystems
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

            # Prepare frame
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_timestamp_ms = (current_time - self.start_time) * 1000
            
            # Check FPS safety threshold
            fps = 1 / dt if dt > 0 else 0
            if fps < config.FAILSAFE_FPS and (current_time - self.start_time) > 2.0:
                self._display_safety_message(img, "LOW FPS")
                continue

            # Process hand detection
            detection_result = self.tracker.process(img_rgb, frame_timestamp_ms)
            
            if detection_result and detection_result.hand_landmarks:
                self._process_hand_detected(
                    detection_result, img, classifier, smoother, cursor, hud, 
                    current_time, dt
                )
            else:
                self._process_hand_lost(cursor, hud, img)
            
            # Display FPS and show frame
            fps = 1 / dt if dt > 0 else 0
            cv2.putText(img, f"{config.APP_NAME} | FPS: {int(fps)}", 
                       (20, 30), cv2.FONT_HERSHEY_PLAIN, 1, (200, 255, 200), 1)
            cv2.imshow(config.APP_NAME, img)

            # Handle keyboard input
            self._handle_input(cursor)

        self.cap.release()
        cv2.destroyAllWindows()
    
    def _process_hand_detected(self, detection_result, img, classifier, smoother, 
                               cursor, hud, current_time, dt):
        """Handle frame with hand detected"""
        hand_landmarks = detection_result.hand_landmarks[0]
        
        # Extract hand position (Index MCP - stable point)
        raw_point = hand_landmarks[5]
        norm_x, norm_y = raw_point.x, raw_point.y
        
        # Smooth hand position
        filtered_pos = smoother(current_time, [norm_x, norm_y])
        curr_x, curr_y = filtered_pos[0], filtered_pos[1]
        
        # Calculate movement delta
        if self.prev_hand_x is not None:
            delta_x = curr_x - self.prev_hand_x
            delta_y = curr_y - self.prev_hand_y
        else:
            delta_x = delta_y = 0.0
        
        self.prev_hand_x = curr_x
        self.prev_hand_y = curr_y
        
        # Classify gesture
        state, meta = classifier.process(hand_landmarks)
        confidence = meta.get("confidence", 0.0)
        
        # Execute gesture actions
        self._execute_gesture(state, delta_x, delta_y, dt, cursor, current_time, norm_x, norm_y)
        
        # Display gesture state
        display_state = state
        if cursor.fast_mode and state == "MOVE":
            display_state = "FAST_MOVE"
        
        hud.draw(img, hand_landmarks, display_state, confidence)
    
    def _execute_gesture(self, state, delta_x, delta_y, dt, cursor, current_time, norm_x, norm_y):
        """Execute action based on detected gesture"""
        if state == "FIST":
            self._handle_drag_toggle(current_time, cursor)
        
        if self.drag_active:
            if state in ["MOVE", "IDLE", "FIST"]:
                cursor.update_relative(delta_x, delta_y, dt)
        else:
            if state == "MOVE":
                cursor.update_relative(delta_x, delta_y, dt)
            elif state == "CLICK_LEFT" and self._check_cooldown(self.last_click_time, current_time):
                pyautogui.click()
                self.last_click_time = current_time
            elif state == "CLICK_RIGHT" and self._check_cooldown(self.last_click_time, current_time):
                pyautogui.rightClick()
                self.last_click_time = current_time
            elif state == "SCROLL":
                self._handle_scroll(norm_y)
    
    def _handle_drag_toggle(self, current_time, cursor):
        """Toggle drag mode on/off"""
        if (current_time - self.last_toggle_time) > config.DRAG_TOGGLE_COOLDOWN:
            self.drag_active = not self.drag_active
            self.last_toggle_time = current_time
            
            if self.drag_active:
                pyautogui.mouseDown()
            else:
                pyautogui.mouseUp()
    
    def _handle_scroll(self, norm_y):
        """Handle scroll gesture"""
        if self.last_scroll_y is not None:
            dy = norm_y - self.last_scroll_y
            if abs(dy) > 0.005:
                scroll_amount = int(-dy * config.SCROLL_SPEED * 100)
                pyautogui.scroll(scroll_amount)
        self.last_scroll_y = norm_y
    
    def _check_cooldown(self, last_time, current_time):
        """Check if enough time has passed since last action"""
        return (current_time - last_time) > config.CLICK_COOLDOWN
    
    def _process_hand_lost(self, cursor, hud, img):
        """Handle frame with no hand detected"""
        if self.drag_active:
            pyautogui.mouseUp()
            self.drag_active = False
        
        self.prev_hand_x = None
        self.prev_hand_y = None
        self.last_scroll_y = None
        
        hud.draw(img, None, "IDLE", 0.0)
    
    def _display_safety_message(self, img, message):
        """Display safety message and pause"""
        text = f"SAFETY PAUSE: {message}"
        cv2.putText(img, text, 
                   (config.WINDOW_WIDTH // 2 - 150, config.WINDOW_HEIGHT // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow(config.APP_NAME, img)
        cv2.waitKey(1)
    
    def _handle_input(self, cursor):
        """Handle keyboard input"""
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.running = False
        elif key == ord('f'):
            cursor.set_fast_mode(not cursor.fast_mode)
            print(f"Fast mode: {'ON' if cursor.fast_mode else 'OFF'}")
