import sys
import requests
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, QThread, QObject
import time
import logging

logging.basicConfig(level=logging.DEBUG)


class CoordinateFetcher(QObject):
    coordinates_updated = pyqtSignal(float, float)  # Signal to send updated coordinates
    error_occurred = pyqtSignal(str)  # Signal for errors
    stop_thread = pyqtSignal()  # Signal to stop the thread

    def __init__(self, object_name):
        super().__init__()
        self.object_name = object_name
        self.running = True

    def fetch_coordinates(self):
        try:
            while self.running:
                url = f"http://localhost:8090/api/objects/info?name={self.object_name}&format=json"
                response = requests.get(url)

                if response.status_code != 200:
                    raise Exception(f"Failed to connect to Stellarium: {response.status_code}")

                data = response.json()
                if 'error' in data:
                    raise Exception(f"Object not found: {data['error']}")

                azimuth = data['azimuth']
                altitude = data['altitude']

                self.coordinates_updated.emit(azimuth, altitude)
                time.sleep(1)  # Fetch updates every second
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.running = False


class MainWindow(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stellarium Object Query")
        self.setGeometry(100, 100, 400, 200)

        # Input for object name
        self.object_name_input = QLineEdit(self)
        self.object_name_input.setPlaceholderText("Enter celestial object name")
        self.object_name_input.setGeometry(10, 50, 250, 30)

        # Button to fetch object coordinates
        self.search_button = QPushButton("Search", self)
        self.search_button.setGeometry(270, 50, 80, 30)
        self.search_button.clicked.connect(self.start_fetching)

        # Label to display azimuth and altitude
        self.output_label = QLabel(self)
        self.output_label.setGeometry(10, 100, 350, 30)
        self.output_label.setText("Azimuth: N/A, Altitude: N/A")

        # Thread and worker
        self.thread = None
        self.worker = None

    def start_fetching(self):
        object_name = self.object_name_input.text().strip()
        if not object_name:
            self.output_label.setText("Error: Please enter a celestial object name.")
            return

        # Stop any existing thread
        if self.thread and self.thread.isRunning():
            self.stop_fetching()

        # Set up the thread and worker
        self.thread = QThread()
        self.worker = CoordinateFetcher(object_name)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.worker.coordinates_updated.connect(self.update_coordinates)
        self.worker.error_occurred.connect(self.handle_error)
        self.thread.started.connect(self.worker.fetch_coordinates)
        self.worker.stop_thread.connect(self.thread.quit)

        # Start the thread
        self.thread.start()

    def update_coordinates(self, azimuth, altitude):
        self.output_label.setText(f"Azimuth: {azimuth:.2f}, Altitude: {altitude:.2f}")

    def handle_error(self, error_message):
        self.output_label.setText(f"Error: {error_message}")
        self.stop_fetching()

    def stop_fetching(self):
        if self.worker:
            self.worker.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait()

    def closeEvent(self, event):
        self.stop_fetching()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())