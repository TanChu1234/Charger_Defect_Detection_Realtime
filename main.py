import sys
from PySide6.QtWidgets import QApplication
from UI.Main_Window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Ensure camera is closed when application exits
    app.aboutToQuit.connect(window.close_devices)
    sys.exit(app.exec())