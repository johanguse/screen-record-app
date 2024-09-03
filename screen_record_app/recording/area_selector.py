from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QColor, QPainter, QPen

class AreaSelector(QWidget):
    area_selected = pyqtSignal(dict)
    BORDER_WIDTH = 2 

    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.start_point = None
        self.current_end_point = None
        self.setup_geometry()
        print("AreaSelector initialized")

    def setup_geometry(self):
        # Set geometry to cover all screens
        combined_geometry = QRect()
        for screen in QApplication.screens():
            combined_geometry = combined_geometry.united(screen.geometry())
        self.setGeometry(combined_geometry)
        print(f"AreaSelector geometry: {self.geometry()}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 50))  # Very slight tint
        painter.drawRect(self.rect())

        if self.start_point and self.current_end_point:
            selection_rect = QRect(self.start_point, self.current_end_point).normalized()
            
            # Draw the semi-transparent fill
            painter.setBrush(QColor(0, 120, 215, 20))  # Light blue with 20% opacity
            painter.drawRect(selection_rect)
            
            # Draw the border
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(0, 120, 215), self.BORDER_WIDTH, Qt.PenStyle.SolidLine))
            painter.drawRect(selection_rect)
            
            print(f"Painting selection rect: {selection_rect}")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.current_end_point = self.start_point
            self.update()
            print(f"Mouse press event: {self.start_point}")

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_point:
            self.current_end_point = event.position().toPoint()
            self.update()
            print(f"Mouse move event: {self.current_end_point}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            end_point = event.position().toPoint()
            selected_area = QRect(self.start_point, end_point).normalized()
            global_start = self.mapToGlobal(selected_area.topLeft())
            self.area_selected.emit({
                "top": global_start.y(),
                "left": global_start.x(),
                "width": selected_area.width(),
                "height": selected_area.height()
            })
            print(f"Selected area: {selected_area}")
            self.close()

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()
        print("AreaSelector shown")

    @staticmethod
    def get_monitor_list():
        return QApplication.screens()

    @staticmethod
    def get_monitor_geometry(monitor_index):
        screens = AreaSelector.get_monitor_list()
        if 0 <= monitor_index < len(screens):
            geometry = screens[monitor_index].geometry()
            return {
                "top": geometry.top(),
                "left": geometry.left(),
                "width": geometry.width(),
                "height": geometry.height()
            }
        return None