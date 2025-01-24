import pytest
from PyQt6.QtCore import QPoint, QRect
from screen_record_app.recording.area_selector import AreaSelector

def test_global_coordinate_conversion(qtbot):
    selector = AreaSelector()
    selector.setGeometry(QRect(-1920, 0, 3840, 1080))  # Simulate dual monitor setup
    
    # Simulate selection in secondary monitor
    start = QPoint(100, 100)  # Widget-relative
    end = QPoint(300, 300)
    
    global_start = selector.mapToGlobal(start)  # Should be (-1920+100, 0+100)
    global_end = selector.mapToGlobal(end)
    
    assert global_start.x() == -1820
    assert global_start.y() == 100
    assert global_end.x() == -1620
    assert global_end.y() == 300 