from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QCheckBox, QRadioButton
from PyQt6.QtCore import Qt

class WebcamControls(QGroupBox):
    def __init__(self, webcam_handler):
        super().__init__("Webcam Options")
        self.webcam_handler = webcam_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.webcam_checkbox = QCheckBox('Enable Webcam')
        self.webcam_checkbox.stateChanged.connect(self.toggle_webcam)
        layout.addWidget(self.webcam_checkbox)

        position_layout = QHBoxLayout()
        positions = [
            ('Top Left', 'top-left'),
            ('Top Right', 'top-right'),
            ('Bottom Left', 'bottom-left'),
            ('Bottom Right', 'bottom-right')
        ]
        
        for label, position in positions:
            radio_button = QRadioButton(label)
            radio_button.toggled.connect(lambda checked, pos=position: self.set_webcam_position(pos) if checked else None)
            position_layout.addWidget(radio_button)
            if position == 'top-right':
                radio_button.setChecked(True)

        layout.addLayout(position_layout)
        self.setLayout(layout)

    def toggle_webcam(self, state):
        is_checked = self.webcam_checkbox.isChecked()
        print(f"Webcam checkbox state changed: {state}, Is checked: {is_checked}")
        self.webcam_handler.toggle_webcam(is_checked)

    def set_webcam_position(self, position):
        self.webcam_handler.set_webcam_position(position)