import json
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import os

# Global state dictionary shared between gesture loop and web server
SHARED_STATE = {
    "hands": [],
    "state": "IDLE",
    "dual_state": "NONE",
    "cursor": {"x": 0.5, "y": 0.5},
    "is_pinching": False,
    "pinch_dist": 0.1,
    "dual_dist": 0.3,
    "dual_angle": 0.0,
    "fps": 60,
    "profile": "DEFAULT",
    "active_window": "",
    "timestamp": 0
}

class SpatialBridgeHandler(BaseHTTPRequestHandler):
    """Handles HTTP and Server-Sent Events (SSE) for the Spatial Node Web UI in multi-threaded mode"""

    def handle(self):
        """Catch and cleanly ignore aborted socket connections from browser closing tabs"""
        try:
            super().handle()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception:
            pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        except Exception:
            pass

    def do_GET(self):
        try:
            # Serve JSON API state
            if self.path == '/api/state':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(SHARED_STATE).encode('utf-8'))
                return

            # Serve SSE live event stream (Threaded per client, 30 FPS update)
            elif self.path == '/api/stream':
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                server_obj = getattr(self, "server", None)
                while server_obj and getattr(server_obj, "running", True):
                    data = f"data: {json.dumps(SHARED_STATE)}\n\n"
                    self.wfile.write(data.encode('utf-8'))
                    self.wfile.flush()
                    time.sleep(0.033)
                return

            # Serve spatial_nodes.html
            elif self.path == '/' or self.path.startswith('/nodes') or self.path.endswith('.html'):
                html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web', 'spatial_nodes.html')
                if os.path.exists(html_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    with open(html_path, 'rb') as f:
                        self.wfile.write(f.read())
                    return

            self.send_response(404)
            self.end_headers()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception:
            pass

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging in terminal
        pass

class SpatialWebServer:
    """Lightweight multi-threaded web server running on port 8765"""
    PORT = 8765

    def __init__(self):
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            return
        try:
            self.server = ThreadingHTTPServer(('127.0.0.1', self.PORT), SpatialBridgeHandler)
            self.server.running = True
            self.running = True
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"[SpatialBridge] Interactive Node Canvas available at: http://127.0.0.1:{self.PORT}")
        except Exception as e:
            print(f"[SpatialBridge] Web Bridge note: {e}")

    def update_state(self, **kwargs):
        """Update shared state sent to connected browser clients"""
        SHARED_STATE.update(kwargs)
        SHARED_STATE["timestamp"] = time.time()

    def stop(self):
        self.running = False
        if self.server:
            try:
                self.server.running = False
                self.server.shutdown()
            except Exception:
                pass
            self.server = None
