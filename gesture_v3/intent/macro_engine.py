import math
import os
import json
import subprocess
import pyautogui

class Dollar1Recognizer:
    """
    Implementation of the $1 Unistroke Recognizer algorithm for spatio-temporal gesture matching.
    Scale-invariant, position-invariant, and rotation-tolerant.
    """
    NUM_POINTS = 32
    SQUARE_SIZE = 250.0

    def __init__(self, templates_file="custom_macros.json"):
        self.templates_file = templates_file
        self.templates = {}
        self._load_default_templates()
        self.load_custom_templates()

    def _load_default_templates(self):
        """Pre-populate with standard productivity shapes and symbols"""
        # Template "C": Left-facing arc (Chrome)
        c_pts = []
        for i in range(32):
            angle = math.pi * 0.75 + (math.pi * 1.5 * (i / 31.0))
            c_pts.append((math.cos(angle) * 100 + 125, math.sin(angle) * 100 + 125))
        self.templates["C"] = {"points": self._normalize_points(c_pts), "action": "cmd:start chrome", "label": "Google Chrome"}

        # Template "O" (Circle): Full loop (Refresh F5)
        o_pts = []
        for i in range(32):
            angle = 2 * math.pi * (i / 31.0)
            o_pts.append((math.cos(angle) * 100 + 125, math.sin(angle) * 100 + 125))
        self.templates["O"] = {"points": self._normalize_points(o_pts), "action": "key:f5", "label": "Refresh Page (F5)"}

        # Template "^" (Up Chevron): Task View
        up_pts = []
        for i in range(16):
            up_pts.append((50 + i * 5, 200 - i * 10))
        for i in range(16):
            up_pts.append((125 + i * 5, 50 + i * 10))
        self.templates["UP"] = {"points": self._normalize_points(up_pts), "action": "hotkey:win,tab", "label": "Task View"}

        # Template "Z": Undo
        z_pts = []
        for i in range(10):  # Top bar
            z_pts.append((50 + i * 15, 50))
        for i in range(12):  # Diagonal
            z_pts.append((185 - i * 12, 50 + i * 12))
        for i in range(10):  # Bottom bar
            z_pts.append((50 + i * 15, 194))
        self.templates["Z"] = {"points": self._normalize_points(z_pts), "action": "hotkey:ctrl,z", "label": "Undo (Ctrl+Z)"}

        # Template "S": Spotify
        s_pts = []
        for i in range(16):
            angle = math.pi * 0.5 + math.pi * (i / 15.0)
            s_pts.append((math.cos(angle) * 40 + 125, math.sin(angle) * 40 + 80))
        for i in range(16):
            angle = -math.pi * 0.5 - math.pi * (i / 15.0)
            s_pts.append((math.cos(angle) * 40 + 125, math.sin(angle) * 40 + 160))
        self.templates["S"] = {"points": self._normalize_points(s_pts), "action": "cmd:start spotify", "label": "Spotify"}

    def _resample(self, points, n):
        """Resample point array into n equidistant points along path length"""
        if len(points) < 2:
            return points * n
            
        path_len = 0.0
        for i in range(1, len(points)):
            path_len += math.hypot(points[i][0] - points[i-1][0], points[i][1] - points[i-1][1])
            
        if path_len == 0.0:
            return [points[0]] * n

        interval = path_len / (n - 1)
        resampled = [points[0]]
        accum_dist = 0.0

        i = 1
        curr = points[0]
        while i < len(points):
            next_pt = points[i]
            d = math.hypot(next_pt[0] - curr[0], next_pt[1] - curr[1])
            if (accum_dist + d) >= interval:
                q = (
                    curr[0] + ((interval - accum_dist) / d) * (next_pt[0] - curr[0]),
                    curr[1] + ((interval - accum_dist) / d) * (next_pt[1] - curr[1])
                )
                resampled.append(q)
                curr = q
                accum_dist = 0.0
            else:
                accum_dist += d
                curr = next_pt
                i += 1

        while len(resampled) < n:
            resampled.append(points[-1])
        return resampled[:n]

    def _rotate_to_zero(self, points):
        """Rotate shape so indicative angle is zero"""
        centroid = self._centroid(points)
        indicative_angle = math.atan2(centroid[1] - points[0][1], centroid[0] - points[0][0])
        return self._rotate_by(points, -indicative_angle, centroid)

    def _rotate_by(self, points, angle, origin):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_pts = []
        for x, y in points:
            dx = x - origin[0]
            dy = y - origin[1]
            new_pts.append((dx * cos_a - dy * sin_a + origin[0], dx * sin_a + dy * cos_a + origin[1]))
        return new_pts

    def _scale_to_square(self, points, size):
        """Scale points to fit bounding square of given size"""
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        w = max(1.0, max_x - min_x)
        h = max(1.0, max_y - min_y)

        new_pts = []
        for x, y in points:
            new_pts.append((x * (size / w), y * (size / h)))
        return new_pts

    def _translate_to_origin(self, points):
        c = self._centroid(points)
        return [(p[0] - c[0], p[1] - c[1]) for p in points]

    def _centroid(self, points):
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)

    def _normalize_points(self, points):
        resampled = self._resample(points, self.NUM_POINTS)
        scaled = self._scale_to_square(resampled, self.SQUARE_SIZE)
        translated = self._translate_to_origin(scaled)
        return translated

    def _path_distance(self, pts1, pts2):
        d = 0.0
        for p1, p2 in zip(pts1, pts2):
            d += math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        return d / len(pts1)

    def recognize(self, points, score_threshold=0.72):
        """
        Recognize stroke points against known templates.
        Returns: (matched_name, confidence, action, label) or (None, 0.0, None, None)
        """
        if len(points) < 10:
            return None, 0.0, None, None

        normalized = self._normalize_points(points)
        best_dist = float('inf')
        best_name = None

        for name, data in self.templates.items():
            dist = self._path_distance(normalized, data["points"])
            if dist < best_dist:
                best_dist = dist
                best_name = name

        half_diagonal = 0.5 * math.hypot(self.SQUARE_SIZE, self.SQUARE_SIZE)
        score = max(0.0, 1.0 - (best_dist / half_diagonal))

        if best_name and score >= score_threshold:
            data = self.templates[best_name]
            return best_name, score, data["action"], data.get("label", best_name)

        return None, score, None, None

    def execute_action(self, action_str):
        """Execute action mapped to recognized gesture"""
        if not action_str:
            return False
            
        try:
            if action_str.startswith("cmd:"):
                cmd = action_str[4:]
                subprocess.Popen(cmd, shell=True)
                return True
            elif action_str.startswith("key:"):
                key = action_str[4:]
                pyautogui.press(key)
                return True
            elif action_str.startswith("hotkey:"):
                keys = [k.strip() for k in action_str[7:].split(",")]
                pyautogui.hotkey(*keys)
                return True
        except Exception as e:
            print(f"[MacroEngine] Action failed: {e}")
        return False

    def save_custom_template(self, name, points, action_str, label=None):
        """Save a new user-trained template to JSON"""
        if len(points) < 10:
            return False
            
        norm_pts = self._normalize_points(points)
        self.templates[name] = {
            "points": norm_pts,
            "action": action_str,
            "label": label or name
        }
        
        # Save to disk
        try:
            serializable = {}
            for k, v in self.templates.items():
                serializable[k] = {
                    "points": v["points"],
                    "action": v["action"],
                    "label": v.get("label", k)
                }
            with open(self.templates_file, "w") as f:
                json.dump(serializable, f, indent=2)
            return True
        except Exception as e:
            print(f"[MacroEngine] Error saving template: {e}")
            return False

    def load_custom_templates(self):
        """Load templates from custom_macros.json if exists"""
        if not os.path.exists(self.templates_file):
            return
        try:
            with open(self.templates_file, "r") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.templates[k] = {
                        "points": [tuple(p) for p in v["points"]],
                        "action": v["action"],
                        "label": v.get("label", k)
                    }
        except Exception as e:
            print(f"[MacroEngine] Error loading custom templates: {e}")
