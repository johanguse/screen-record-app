from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton

class ExportControls(QWidget):
    def __init__(self, video_exporter, main_window):
        super().__init__()
        self.video_exporter = video_exporter
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems(['mp4', 'avi'])
        self.enhance_checkbox = QCheckBox('Enhance with AI')
        self.export_button = QPushButton('Export')
        self.export_button.clicked.connect(self.start_export)

        layout.addWidget(QLabel('Export Format:'))
        layout.addWidget(self.format_combo)
        layout.addWidget(self.enhance_checkbox)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def start_export(self):
        output_format = self.format_combo.currentText()
        enhance = self.enhance_checkbox.isChecked()
        frames = self.main_window.frames
        audio_data = self.main_window.audio_recorder.audio_data
        self.video_exporter.start_export(frames, audio_data, output_format, enhance)