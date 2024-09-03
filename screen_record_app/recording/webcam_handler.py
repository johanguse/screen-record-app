import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from screen_record_app.utils.image_processing import overlay_webcam

class WebcamThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = True

    def run(self):
        print("Starting webcam thread...")
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Failed to open webcam.")
                return
            print("Webcam opened successfully.")
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    self.changePixmap.emit(qt_image)
                else:
                    print("Failed to read frame from webcam.")
        except Exception as e:
            print(f"Exception in webcam thread: {e}")
        finally:
            if self.cap:
                self.cap.release()
            print("Webcam thread finished.")

    def stop(self):
        print("Stopping webcam thread...")
        self.running = False
        self.quit()
        self.wait()

class WebcamHandler:
    def __init__(self):
        self.webcam_thread = WebcamThread()
        self.webcam_thread.changePixmap.connect(self.update_frame)
        self.webcam_position = 'top-right'
        self.is_enabled = False
        self.current_frame = None

    def toggle_webcam(self, state):
        print(f"Toggling webcam. State: {state}")
        self.is_enabled = state
        if self.is_enabled:
            print("Starting webcam...")
            self.webcam_thread.start()
        else:
            print("Stopping webcam...")
            self.webcam_thread.stop()

    def update_frame(self, frame):
        print("Updating frame from webcam...")
        self.current_frame = frame

    def overlay_webcam(self, frame):
        if self.is_enabled and self.current_frame:
            # Convert QImage to OpenCV format
            webcam_frame = self.qimage_to_cv2(self.current_frame)
            frame = overlay_webcam(frame, webcam_frame, self.webcam_position)
        return frame

    def qimage_to_cv2(self, qimage):
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        width, height = qimage.width(), qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 3)
        arr = np.array(ptr).reshape(height, width, 3)
        # Convert RGB to BGR
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    def set_webcam_position(self, position):
        self.webcam_position = position

    def release_webcam(self):
        self.webcam_thread.stop()