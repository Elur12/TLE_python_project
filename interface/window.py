from PyQt5 import QtWidgets, uic, QtCore, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QSlider, QVBoxLayout, QScrollArea
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.window = None

        self.initUI()

    def initUI(self):
        self.window = uic.loadUi("main_window.ui", self)

        self.window.setWindowTitle("Трекинг спутников на базе TLE данных")

        self.tabWidget.addTab(self.tabTracking, 'Tracking')
        self.tabTracking.layout = QVBoxLayout()

        self.vertical_layout_main = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea()

        content_widget = QtWidgets.QWidget()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)

        for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            btn = QtWidgets.QPushButton(l)
            self.vertical_layout_main.addWidget(btn)
        self.vertical_layout_main.addStretch()

        scroll.setFixedHeight(400)

        self.vertical_layout_main.addWidget(scroll)
        self.tabTracking.layout.addWidget(self.vertical_layout_main)

        '''
        widget = QWidget()
        layout = QVBoxLayout(self)
        for _ in range(20):
            btn = QPushButton("test")
            layout.addWidget(btn)
        widget.setLayout(layout)

        self.tabWidget.addWidget(layout)

        
        # Scroll Area Properties
        scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        # Scroll Area Layer add
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)
        '''


def window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()