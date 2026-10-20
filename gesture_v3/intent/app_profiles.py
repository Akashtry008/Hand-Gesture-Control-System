import time
import pyautogui

try:
    import pygetwindow as gw
except ImportError:
    gw = None

class AppProfileManager:
    """
    Context-Aware Application Profile Switcher ("Air StreamDeck").
    Detects the active foreground application window and adapts gesture interpretation
    specifically for Media, PowerPoint Presentations, Web Browsers, or Desktop.
    """
    def __init__(self):
        self.current_profile = "DEFAULT"
        self.active_window_title = ""
        self.last_check_time = 0.0
        self.check_interval = 0.5  # Check window title every 500ms to reduce OS overhead

    def update(self):
        """Check active window and return current profile name"""
        now = time.time()
        if now - self.last_check_time < self.check_interval:
            return self.current_profile, self.active_window_title

        self.last_check_time = now
        title = ""
        if gw is not None:
            try:
                active_win = gw.getActiveWindow()
                if active_win and active_win.title:
                    title = active_win.title
            except Exception:
                title = ""

        self.active_window_title = title
        lower_title = title.lower()

        # 1. Media Profile
        media_keywords = ["spotify", "vlc", "youtube", "netflix", "music", "prime video", "soundcloud"]
        if any(k in lower_title for k in media_keywords):
            self.current_profile = "MEDIA"
            return self.current_profile, title

        # 2. Presentation Profile (PowerPoint, PDF, Slides)
        present_keywords = ["powerpoint", "slides", "keynote", "acrobat", "pdf", "presentation"]
        if any(k in lower_title for k in present_keywords):
            self.current_profile = "PRESENTATION"
            return self.current_profile, title

        # 3. Browser / Developer Profile
        browser_keywords = ["chrome", "firefox", "edge", "brave", "visual studio code", "pycharm", "sublime"]
        if any(k in lower_title for k in browser_keywords):
            self.current_profile = "BROWSER"
            return self.current_profile, title

        # 4. Default Desktop Profile
        self.current_profile = "DEFAULT"
        return self.current_profile, title

    def handle_profile_action(self, profile, gesture_state, hud, current_time):
        """
        Execute profile-specific custom actions.
        Returns True if handled specifically by the profile, False to fall back to default.
        """
        if profile == "PRESENTATION":
            # Slide Next / Previous
            if gesture_state == "NEXT_TRACK":
                pyautogui.press('right')
                hud.trigger_notification("➡️ SLIDE NEXT", (0, 255, 100), duration=0.6)
                return True
            elif gesture_state == "PREV_TRACK":
                pyautogui.press('left')
                hud.trigger_notification("⬅️ SLIDE PREVIOUS", (0, 255, 100), duration=0.6)
                return True
            elif gesture_state == "FIST":
                # Toggle black screen in PowerPoint
                pyautogui.press('b')
                hud.trigger_notification("⬛ BLACKOUT SCREEN", (50, 50, 50), duration=0.8)
                return True

        elif profile == "BROWSER":
            # Tab cycling with track gestures
            if gesture_state == "NEXT_TRACK":
                pyautogui.hotkey('ctrl', 'tab')
                hud.trigger_notification("📑 NEXT TAB", (0, 200, 255), duration=0.4)
                return True
            elif gesture_state == "PREV_TRACK":
                pyautogui.hotkey('ctrl', 'shift', 'tab')
                hud.trigger_notification("📑 PREVIOUS TAB", (0, 200, 255), duration=0.4)
                return True

        return False
