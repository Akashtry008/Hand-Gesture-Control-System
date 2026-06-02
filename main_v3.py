"""
Project Air - Hand Gesture Control System
Main entry point. Run this to start the application.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gesture_v3.core.system import SystemController

if __name__ == "__main__":
    app = SystemController()
    app.run()
