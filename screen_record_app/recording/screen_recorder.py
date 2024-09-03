import numpy as np
from mss import mss
import cv2

class ScreenRecorder:
    def __init__(self, frame_rate=10):
        self.sct = mss()
        self.recording_area = None
        self.is_recording = False
        self.frame_rate = frame_rate

    def capture_frame(self, force=False):
        if not self.is_recording and not force:
            return None

        try:
            if self.recording_area:
                screenshot = np.array(self.sct.grab(self.recording_area))
            else:
                screenshot = np.array(self.sct.grab(self.sct.monitors[0]))
            
            if screenshot.size == 0:
                return None

            # Ensure the color conversion is correct
            if screenshot.shape[2] == 4:  # BGRA format
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            elif screenshot.shape[2] == 3:  # BGR format
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGR)
            return screenshot
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    def start_recording(self):
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False

    def set_recording_area(self, area):
        self.recording_area = area