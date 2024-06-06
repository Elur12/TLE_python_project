import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, uic, QtCore, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QSlider, QVBoxLayout, QScrollArea, \
    QTabWidget, QDialog, QTableWidget, QHBoxLayout, QSplitter, QTextEdit, QFrame, QCheckBox, QTableWidgetItem
from PyQt5.QtGui import QPixmap
import sys
import satelite

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Трекинг спутников на базе TLE данных")
        self.setMinimumSize(630, 600)
        self.resize(630, 300)

        vbox = QVBoxLayout()
        tab_widget = QTabWidget()

        tab_widget.addTab(TabTracking(), "Tracking")
        tab_widget.addTab(TabWorldMap(), "World Map")
        tab_widget.addTab(TabSchedule(), "Schedule")
        tab_widget.addTab(TabSettings(), "Settings")

        vbox.addWidget(tab_widget)

        self.setLayout(vbox)

class TabTracking(QWidget):
    def __init__(self):
        super().__init__()

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)

        label_updated = QLabel("updated time: ")
        label_time = QLabel("test", right_frame)
        update_button = QPushButton("Update", right_frame)

        vbox_right = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(1)
        table.setRowCount(10)
        table.setHorizontalHeaderLabels(["Satellites"])

        # Расстановка спутников
        item = QTableWidgetItem("NOAA19")
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        table.setItem(0, 0, item)

        item = QTableWidgetItem("METOP_B")
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        table.setItem(1, 0, item)

        vbox_right.addWidget(table)
        vbox_right.addWidget(label_updated)
        vbox_right.addWidget(label_time)
        vbox_right.addWidget(update_button)

        right_frame.setLayout(vbox_right)

        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(QtCore.Qt.Horizontal)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)

        hbox = QHBoxLayout(self)
        hbox.addWidget(splitter)
        self.setLayout(hbox)

class TabWorldMap(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        update_button = QPushButton("Update")
        vbox.addWidget(update_button)

        self.setLayout(vbox)

class TabSchedule(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setRowCount(1)

        table.setHorizontalHeaderLabels(["Name", "Time of start", "Time of stop", "Apogey"])

        vbox.addWidget(table)

        self.setLayout(vbox)

class TabSettings(QWidget):
    def __init__(self):
        super().__init__()


def window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()