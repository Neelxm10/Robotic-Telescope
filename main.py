import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class TelescopeControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout with margins and spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Camera frame layout with centered alignment
        image_layout = QVBoxLayout()
        image_layout.setSpacing(10)

        # Label to display the camera frame, with a fixed size and centered alignment
        self.image_label = QLabel("Camera Frame")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(400, 300)  # Set fixed size for image
        self.image_label.setStyleSheet("border: 2px solid black; background-color: #f0f0f0; color: #333;")
        image_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Add the image layout to the main layout
        layout.addLayout(image_layout)

        # Buttons layout with full-width, resizable buttons
        button_layout = QGridLayout()
        button_layout.setSpacing(10)

        # Create buttons with size policies that ensure the full text is displayed, and add some color
        self.manual_control_btn = QPushButton('Manual Motion Control')
        self.manual_control_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.manual_control_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.manual_control_btn.clicked.connect(self.manual_control)
        button_layout.addWidget(self.manual_control_btn, 0, 0)

        self.capture_image_btn = QPushButton('Capture Image')
        self.capture_image_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.capture_image_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.capture_image_btn.clicked.connect(self.capture_image)
        button_layout.addWidget(self.capture_image_btn, 0, 1)

        self.image_library_btn = QPushButton('Show Image Library')
        self.image_library_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.image_library_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.image_library_btn.clicked.connect(self.show_image_library)
        button_layout.addWidget(self.image_library_btn, 1, 0)

        self.classify_image_btn = QPushButton('Classify Image')
        self.classify_image_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.classify_image_btn.setStyleSheet("background-color: #9C27B0; color: white;")
        self.classify_image_btn.clicked.connect(self.classify_image)
        button_layout.addWidget(self.classify_image_btn, 1, 1)

        self.calibration_btn = QPushButton('Calibration')
        self.calibration_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.calibration_btn.setStyleSheet("background-color: #607D8B; color: white;")
        button_layout.addWidget(self.calibration_btn, 2, 0, 1, 2)  # Spans two columns

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        # Set layout and window title
        self.setLayout(layout)
        self.setWindowTitle('Telescope Control System')
        self.setStyleSheet("background-color: #e0e0e0;")  # Softer background color
        self.resize(600, 600)  # Set a larger window size to accommodate all widgets

    # Placeholder functions for each feature
    def manual_control(self):
        print("Manual control initiated")

    def capture_image(self):
        print("Image captured")
        # You can integrate actual camera logic here

    def show_image_library(self):
        print("Displaying image library")
        options = QFileDialog.Options()
        file_dialog = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_dialog:
            image_path = file_dialog[0]
            self.display_image(image_path)

    def classify_image(self):
        print("Classifying image using neural network")
        # You can integrate TensorFlow/PyTorch classification logic here

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TelescopeControlUI()
    window.show()
    sys.exit(app.exec_())