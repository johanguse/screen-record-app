import cv2
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from screen_record_app.recording.audio_recorder import AudioRecorder
from screen_record_app.recording.screen_recorder import ScreenRecorder
from screen_record_app.recording.webcam_handler import WebcamHandler
from screen_record_app.export.video_exporter import VideoExporter
from screen_record_app.utils.image_processing import create_qimage
from screen_record_app.ui.recording_controls import RecordingControls
from screen_record_app.ui.webcam_controls import WebcamControls
from screen_record_app.ui.export_controls import ExportControls
from screen_record_app.ui.timeline import Timeline
from screen_record_app.ui.preview_thread import PreviewThread
from collections import deque

class CaptureCanvasPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_components()
        self.init_ui()
        self.start_preview()  # Start the preview thread when the application initializes

    def init_components(self):
        self.audio_recorder = AudioRecorder()
        self.screen_recorder = ScreenRecorder()
        self.webcam_handler = WebcamHandler()
        self.video_exporter = VideoExporter()
        self.video_exporter.export_progress.connect(self.update_export_progress)
        self.video_exporter.export_completed.connect(self.export_completed)
        self.video_exporter.export_error.connect(self.export_error)
        self.frames = deque(maxlen=100)
        self.current_frame = 0

        self.preview_thread = PreviewThread(
            screen_recorder_params={'recording_area': None},
            webcam_handler=self.webcam_handler
        )
        self.preview_thread.frame_ready.connect(self.update_preview_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_frame)

    def init_ui(self):
        self.setWindowTitle('CaptureCanvas Pro')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.preview_label)

        self.recording_controls = RecordingControls(self)
        main_layout.addWidget(self.recording_controls)

        self.webcam_controls = WebcamControls(self.webcam_handler)
        main_layout.addWidget(self.webcam_controls)

        self.export_controls = ExportControls(self.video_exporter, self)
        main_layout.addWidget(self.export_controls)

        self.timeline = Timeline()
        # Corrected the method name to start_preview
        self.timeline.frame_changed.connect(self.start_preview)
        main_layout.addWidget(self.timeline)

        self.status_container = QWidget(self)
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_label = QLabel('Ready to record', self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False)
        self.status_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.status_container)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def start_preview(self):
        if not self.preview_thread.isRunning():
            self.preview_thread.start()

    def stop_preview(self):
        self.preview_thread.stop()

    def capture_frame(self):
        frame = self.screen_recorder.capture_frame(force=True)
        if frame is not None:
            self.frames.append(frame)
            self.update_preview_label(frame)

    def update_preview_label(self, frame):
        q_img = create_qimage(frame)
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_status(self, message):
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        self.progress_bar.setVisible(False)
    
    def start_export(self, output_format):
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        frames = list(self.frames)
        audio_data = self.audio_recorder.get_audio_data()
        enhance = True  # or False, based on user preference
        self.video_exporter.start_export(frames, audio_data, output_format, enhance)

    def update_export_progress(self, progress):
        self.progress_bar.setValue(progress)

    def export_completed(self):
        self.update_status("Export complete")
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(True)

    def export_error(self, error_message):
        self.update_status(f"Export failed: {error_message}")
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(True)

    def closeEvent(self, event):
        print("Closing application...")
        self.webcam_handler.release_webcam()
        self.preview_thread.stop()
        super().closeEvent(event)