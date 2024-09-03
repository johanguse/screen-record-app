from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import pyqtSignal
from screen_record_app.recording.area_selector import AreaSelector

class RecordingControls(QWidget):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_recording = False
        self.area_selector = None
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)

        self.record_button = QPushButton('Start Recording', self)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.area_select_button = QPushButton('Select Area', self)
        self.area_select_button.clicked.connect(self.select_area)
        layout.addWidget(self.area_select_button)

        self.monitor_combo = QComboBox(self)
        self.monitor_combo.addItem('All Screens')
        self.monitor_combo.addItems([f'Monitor {i+1}' for i in range(len(AreaSelector.get_monitor_list()))])
        self.monitor_combo.currentIndexChanged.connect(self.select_monitor)
        layout.addWidget(self.monitor_combo)

        self.setLayout(layout)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.pause_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.setText('Pause Recording')
        self.stop_button.setEnabled(True)
        self.area_select_button.setEnabled(False)
        self.monitor_combo.setEnabled(False)
        self.parent.update_status('Recording...')
        self.parent.screen_recorder.start_recording()
        self.parent.timer.start(33)  # Start the frame capture timer
        self.recording_started.emit()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.setText('Start Recording')
        self.stop_button.setEnabled(False)
        self.area_select_button.setEnabled(True)
        self.monitor_combo.setEnabled(True)
        self.parent.update_status('Recording stopped')
        self.parent.screen_recorder.stop_recording()
        self.parent.timer.stop()
        self.parent.start_preview()  # Restart preview
        self.recording_stopped.emit()

    def pause_recording(self):
        self.is_recording = False
        self.record_button.setText('Resume Recording')
        self.parent.update_status('Paused')

    def select_area(self):
        print("Select Area button clicked")
        self.area_selector = AreaSelector()
        self.area_selector.area_selected.connect(self.on_area_selected)
        self.area_selector.show()

    def on_area_selected(self, area):
        print(f"Area selected in RecordingControls: {area}")
        self.parent.screen_recorder.set_recording_area(area)
        self.monitor_combo.setCurrentIndex(0)
        self.parent.preview_thread.update_params(
            screen_recorder_params={'recording_area': area},
            webcam_handler_params={}
        )
        self.parent.start_preview()  # Restart preview with new area

    def select_monitor(self, index):
        if index == 0:
            self.parent.screen_recorder.set_recording_area(None)
            self.parent.preview_thread.update_params(
                screen_recorder_params={'recording_area': None},
                webcam_handler_params={}
            )
            self.parent.start_preview()  # Restart preview with all screens
        else:
            monitor_geometry = AreaSelector.get_monitor_geometry(index - 1)
            if monitor_geometry:
                area = {
                    "top": monitor_geometry["top"],
                    "left": monitor_geometry["left"],
                    "width": monitor_geometry["width"],
                    "height": monitor_geometry["height"]
                }
                self.parent.screen_recorder.set_recording_area(area)
                self.parent.preview_thread.update_params(
                    screen_recorder_params={'recording_area': area},
                    webcam_handler_params={}
                )
                self.parent.start_preview()  # Restart preview with new monitor
        print(f"Selected monitor: {index}")