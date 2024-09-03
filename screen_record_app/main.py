import sys
from PyQt6.QtWidgets import QApplication
from screen_record_app.ui.main_window import CaptureCanvasPro

def main():
    app = QApplication(sys.argv)
    ex = CaptureCanvasPro()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()