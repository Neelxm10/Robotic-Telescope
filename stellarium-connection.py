import sys
import requests
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from PyQt5.QtTest import QTest
import logging
import socket
from threading import Thread
from bitstring import ConstBitStream

logging.basicConfig(level=logging.DEBUG)


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
        self.search_button.clicked.connect(self.fetch_object_coordinates)

        # Label to display azimuth and altitude
        self.output_label = QLabel(self)
        self.output_label.setGeometry(10, 100, 350, 30)
        self.output_label.setText("Azimuth: N/A, Altitude: N/A")

    def fetch_object_coordinates(self):
        object_name = self.object_name_input.text().strip()
        if object_name:
            try:
                az, alt = self.query_stellarium(object_name)
                self.output_label.setText(f"Azimuth: {az:.2f}, Altitude: {alt:.2f}")
            except Exception as e:
                self.output_label.setText(f"Error: {str(e)}")

    def query_stellarium(self, object_name):
        url = f"http://localhost:8090/api/objects/info?name={object_name}&format=json"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to connect to Stellarium: {response.status_code}")

        data = response.json()
        if 'error' in data:
            raise Exception(f"Object not found: {data['error']}")

        azimuth = data['azimuth']
        altitude = data['altitude']
        return azimuth, altitude


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())