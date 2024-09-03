from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt, pyqtSignal

class Timeline(QSlider):
    frame_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setEnabled(False)
        self.valueChanged.connect(self.frame_changed.emit)

    def set_frame_count(self, count):
        self.setMaximum(count - 1)
        self.setEnabled(count > 0)