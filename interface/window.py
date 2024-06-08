import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, UTC, timedelta
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, uic, QtCore, Qt, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QSlider, QVBoxLayout, QScrollArea, \
    QTabWidget, QDialog, QTableWidget, QHBoxLayout, QSplitter, QTextEdit, QFrame, QCheckBox, QTableWidgetItem, QLineEdit
import sys
from itertools import chain
from PyQt5.QtCore import Qt

matplotlib.use('Qt5Agg')


COLOR_VAL = 12
COLOR_BRIGHTNESS = 1
COLOR_UNBRIGHTNESS = 0.5

COVERAGE_LON = 20

def draw_map(m, scale=0.2):
    # draw a shaded-relief image
    m.shadedrelief(scale=scale)
    
    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))

    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)
    
    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')


selected_items = set()


class MainWindow(QDialog):

    def message(self, item):
        if(item.checkState() == QtCore.Qt.CheckState.Checked):
            selected_items.add(item.text())
        else:
            selected_items.discard(item.text())

    def search(self, s):
        # Clear current selection.
        self.table.setCurrentItem(None)
        if not s:
            # Empty string, don't search.
            return
        matching_items = self.table.findItems(s, Qt.MatchContains)
        if matching_items:
            # We have found something.
            item = matching_items[0]  # Take the first.
            self.table.setCurrentItem(item)
            for item in matching_items:
                item.setSelected(True)

    def __init__(self, sattelites):
        super().__init__()

        self.setWindowTitle("Трекинг спутников на базе TLE данных")
        self.setMinimumSize(1280, 720)
        self.resize(630, 300)

        self.place = [0, 0, 0]

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)

        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)


        label_updated = QLabel("updated time: ")
        label_time = QLabel("test", right_frame)
        update_button = QPushButton("Update", right_frame)

        keys = sorted(list(sattelites.keys()))

        self.query = QLineEdit()
        self.query.setPlaceholderText("Search...")
        self.query.textChanged.connect(self.search)

        doubleSpinBox = QtWidgets.QDoubleSpinBox()
        doubleSpinBox.setGeometry(QtCore.QRect(230, 10, 161, 24))
        doubleSpinBox.setDecimals(6)
        doubleSpinBox.setMinimum(-90.0)
        doubleSpinBox.setMaximum(90.0)
        doubleSpinBox.valueChanged.connect(lambda x: self.update_place(x, 1))

        doubleSpinBox_2 = QtWidgets.QDoubleSpinBox()
        doubleSpinBox_2.setGeometry(QtCore.QRect(230, 40, 161, 24))
        doubleSpinBox_2.setDecimals(6)
        doubleSpinBox_2.setMinimum(-180.0)
        doubleSpinBox_2.setMaximum(180.0)
        doubleSpinBox_2.valueChanged.connect(lambda x: self.update_place(x, 0))

        doubleSpinBox_3 = QtWidgets.QDoubleSpinBox()
        doubleSpinBox_3.setGeometry(QtCore.QRect(230, 40, 161, 24))
        doubleSpinBox_3.setDecimals(3)
        doubleSpinBox_3.valueChanged.connect(lambda x: self.update_place(x, 2))

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setRowCount(len(keys))
        self.table.setHorizontalHeaderLabels(["check","Satellites"])

        # Расстановка спутников
        for i in range(len(keys)):
            item = QTableWidgetItem(keys[i])
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.table.setItem(i, 0, item)
        self.table.itemChanged.connect(self.message)


        tab_widget = QTabWidget()

        tab_widget.addTab(TabTracking(), "Tracking")
        tab_widget.addTab(TabWorldMap(sattelites=sattelites, place=self.place), "World Map")
        tab_widget.addTab(TabSchedule(), "Schedule")
        tab_widget.addTab(TabSettings(), "Settings")
        

        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()
        
        vbox_right.addWidget(self.query)
        vbox_right.addWidget(self.table)
        vbox_right.addWidget(label_updated)
        vbox_right.addWidget(label_time)

        vbox_right.addWidget(QLabel("LON: "))
        vbox_right.addWidget(doubleSpinBox_2)
        vbox_right.addWidget(QLabel("LAT: "))
        vbox_right.addWidget(doubleSpinBox)
        vbox_right.addWidget(QLabel("ALT: "))
        vbox_right.addWidget(doubleSpinBox_3)

        vbox_right.addWidget(update_button)
        

        vbox_left.addWidget(tab_widget)

        right_frame.setLayout(vbox_right)
        left_frame.setLayout(vbox_left)


        splitter = QSplitter(QtCore.Qt.Horizontal)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)

        hbox = QHBoxLayout(self)
        hbox.addWidget(splitter)

        self.setLayout(hbox)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(lambda : self.update_time(label_time))
        self.timer.start()


    def update_time(self, label_time: QLabel):
        label_time.setText(datetime.now(UTC).strftime("%d_%m_%Y %H:%M:%S"))

    def update_place(self, value: float, i: int):
        self.place[i] = value

class TabTracking(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        #self.setCentralWidget(self.canvas)

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Drop off the first y element, append a new one.
        #self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        #self.canvas.axes.cla()  # Clear the canvas.
        #self.canvas.axes.plot(self.xdata, self.ydata, 'r')
        # Trigger the canvas to update and redraw.
        self.canvas.draw()




class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        fig = plt.figure(figsize=(width, height), edgecolor='w')
        self.plt = plt
        super(MplCanvas, self).__init__(fig)

class TabWorldMap(QWidget):
    def __init__(self, sattelites, place):
        super().__init__()
        vbox = QVBoxLayout()

        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)

        self.clear_all()

        self.sattelites = sattelites

        self.old_selected_items = selected_items.copy()

        self.old_scatter = {}
        self.orbit_number = {}
        self.plotes = {}
        self.text = {}
        self.color = {}
        self.color_iter = 0

        self.place_pos = place
        self.old_place_pos = place.copy()
        self.place = self.m.scatter(self.place_pos[0], self.place_pos[1], latlon=True, c = (1,0.5,0.5), alpha=0.5)
        self.text_place = self.canvas.plt.text(self.place_pos[0]+6, self.place_pos[1]+6, "Your Place", fontsize=8, backgroundcolor = (1,1,1,0.7))

        self.update_plot()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

    def clear_all(self):
        self.canvas.figure.clear()
        self.m = Basemap(projection='cyl', resolution=None,
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180, )
        draw_map(self.m)

    def update_plot(self):
        #self.clear()
        update_place = False
        if(self.place_pos != self.old_place_pos):
            self.place.remove()
            self.text_place.remove()

            self.place = self.m.scatter(self.place_pos[0], self.place_pos[1], latlon=True, c = (1,0.5,0.5), alpha=0.5)
            self.text_place = self.canvas.plt.text(self.place_pos[0]+6, self.place_pos[1]+6, "Your Place", fontsize=8, backgroundcolor = (1,1,1,0.7))
            
            self.old_place_pos = self.place_pos.copy()

            update_place = True
        for i in selected_items:
            if(self.color.get(i) == None):
                self.color[i] = rainbow(self.color_iter, COLOR_VAL, COLOR_BRIGHTNESS, COLOR_UNBRIGHTNESS)
                self.color_iter += 1
                if(self.color_iter >= COLOR_VAL*(1/COLOR_UNBRIGHTNESS)*(1/(COLOR_BRIGHTNESS-COLOR_UNBRIGHTNESS))):
                    self.color_iter = 0
            col = self.color.get(i)

            if(self.orbit_number.get(i) != self.sattelites[i].get_orbit_number()):
                self.orbit_number[i] = self.sattelites[i].get_orbit_number()
                l = self.sattelites[i].get_while_loc(deltaseconds = 10)
                l_old = rasdel(l)
                if self.plotes.get(i) != None:
                    for j in self.plotes.get(i):
                        j.remove()
                self.plotes[i] = []
                
                for o in l_old:
                    j,  = self.m.plot(o[0], o[1], c = col)
                    self.plotes[i].append(j)

            if(self.old_scatter.get(i) != None):
                self.old_scatter.get(i).remove()
                self.old_scatter[i] = None
            k = self.sattelites.get(i).get_location()
            self.old_scatter[i] = self.m.scatter(k[0], k[1], latlon=True, c = col, alpha=0.5)
            if(self.text.get(i) != None):
                self.text.get(i).remove()
                self.text[i] = None
            x, y = self.m(k[0], k[1])
            self.text[i] = self.canvas.plt.text(x+6, y+6, i, fontsize=12, backgroundcolor = (0.8,0.8,0.9,0.7))

            if(update_place):
                self.sattelites[i].update_place(self.place_pos)

        for i in self.old_selected_items - selected_items:
            self.old_scatter.get(i).remove()
            for j in self.plotes.get(i):
                j.remove()
            self.plotes[i] = []
            self.old_scatter[i] = None
            self.orbit_number[i] = None
            self.text.get(i).remove()
            self.text[i] = None
        
        for i in selected_items - self.old_selected_items:
            self.sattelites[i].update_place(self.place_pos)

        self.old_selected_items = selected_items.copy()

        self.canvas.draw()

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


def rasdel(l):
    k = []
    k_sorted = []
    kj = [0]
    for i in range(len(l[0]) - 1):
        k.append(abs((l[0][i] - l[0][i+1])))
    k_sorted = sorted(k, reverse=True)
    
    if k_sorted[0] + COVERAGE_LON >= 360:
        kj.append(k.index(k_sorted[0]) + 1)
    if k_sorted[1] + COVERAGE_LON >= 360:
        kj.append(k.index(k_sorted[1]) + 1)

    kj.append(len(l[0]))

    kl = []
    for i in range(len(kj) - 1):
        kl.append([l[0][kj[i]:kj[i+1]],l[1][kj[i]:kj[i+1]]])
    return kl

def rainbow(iter, speed, brightness, unbrightness):
    big_iter = iter // speed 
    brightness = brightness - unbrightness * ((unbrightness*big_iter) // brightness)
    unbrightness = (unbrightness*big_iter) % brightness

    g = lambda i: (abs(3*(i%(speed) - 5/6*speed)/speed) - 0.5)
    r = lambda i: (abs(3*(i%(speed) - 1/2*speed)/speed) - 0.5)
    b = lambda i: (abs(3*(i%(speed) - 1/6*speed)/speed) - 0.5)
    to_formul = lambda i, k: min(1, max(2*(k(i) > 1) + k(i)*(1-2*(k(i) > 1)), 0) * 2)
    return (to_formul(iter, r)*(brightness - unbrightness*big_iter) + big_iter*unbrightness, to_formul(iter, g)*(brightness - unbrightness*big_iter) + big_iter*unbrightness, to_formul(iter, b)*(brightness - unbrightness*big_iter) + big_iter*unbrightness)

def window(sattelites):
    app = QApplication(sys.argv)
    window = MainWindow(sattelites=sattelites)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()