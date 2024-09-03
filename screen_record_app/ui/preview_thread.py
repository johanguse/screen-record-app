from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
import cv2
from screen_record_app.recording.screen_recorder import ScreenRecorder
from screen_record_app.recording.webcam_handler import WebcamHandler

class PreviewThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, screen_recorder_params, webcam_handler):
        super().__init__()
        self.screen_recorder_params = screen_recorder_params
        self.webcam_handler = webcam_handler
        self.running = False

    def run(self):
        self.screen_recorder = ScreenRecorder()
        self.screen_recorder.set_recording_area(self.screen_recorder_params.get('recording_area'))
        self.running = True
        while self.running:
            frame = self.screen_recorder.capture_frame(force=True)
            if frame is not None:
                if self.webcam_handler.is_enabled:
                    frame = self.webcam_handler.overlay_webcam(frame)
                if frame.shape[2] == 4:  # BGRA format
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.frame_ready.emit(frame)
            self.msleep(33)  # Update at ~30 FPS

    def stop(self):
        self.running = False
        self.wait()

    def update_params(self, screen_recorder_params, webcam_handler_params):
        self.screen_recorder_params = screen_recorder_params
        self.webcam_handler_params = webcam_handler_params
        self.screen_recorder.set_recording_area(self.screen_recorder_params.get('recording_area'))