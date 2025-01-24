from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QRect, Qt, pyqtSignal, QPoint
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

            # Add size text display
            painter.setPen(QColor(255, 255, 255))
            text = f"{selection_rect.width()}x{selection_rect.height()}"
            painter.drawText(selection_rect.bottomRight() + QPoint(10, 10), text)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.CrossCursor)  # Add crosshair cursor
            self.start_point = event.position().toPoint()
            self.current_end_point = self.start_point
            self.update()
            print(f"Mouse press event: {self.start_point}")

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_point:
            # Constrain to screen boundaries
            pos = event.position().toPoint()
            screen_rect = self.geometry()
            pos.setX(max(min(pos.x(), screen_rect.right()), screen_rect.left()))
            pos.setY(max(min(pos.y(), screen_rect.bottom()), screen_rect.top()))
            
            self.current_end_point = pos
            self.update()
            print(f"Mouse move event: {self.current_end_point}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            # Convert both points to global coordinates
            global_start = self.mapToGlobal(self.start_point)
            global_end = self.mapToGlobal(event.position().toPoint())
            
            # Create rect from global coordinates
            selected_area = QRect(global_start, global_end).normalized()
            
            if selected_area.width() < 10 or selected_area.height() < 10:
                print("Selection too small, ignoring")
                self.close()
                return
            
            self.area_selected.emit({
                "top": selected_area.top(),
                "left": selected_area.left(),
                "width": selected_area.width(),
                "height": selected_area.height()
            })
            print(f"Selected area: {selected_area.getCoords()}")
            self.close()
            self.setCursor(Qt.CursorShape.ArrowCursor)  # Restore default cursor

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