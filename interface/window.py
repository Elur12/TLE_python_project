import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta, time
# from datetime import UTC
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, Qt, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, \
    QTabWidget, QDialog, QTableWidget, QHBoxLayout, QSplitter, QFrame, QTableWidgetItem, \
    QLineEdit, QHeaderView
import sys
from itertools import chain
from PyQt5.QtCore import Qt

matplotlib.use('Qt5Agg')


COLOR_VAL = 6
COLOR_BRIGHTNESS = 1
COLOR_UNBRIGHTNESS = 0.5

COVERAGE_LON = 20

MAX_ANGLE = 30
HORIZON = 0
DELTA_SECONDS = 0.5

save_to_json = None

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




class MainWindow(QDialog):

    def message(self, item):
        if(item.checkState() == QtCore.Qt.CheckState.Checked):
            self.selected_items.add(item.text())
        else:
            self.selected_items.discard(item.text())
        self.save_to_json(selected_items = self.selected_items)

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
            row = item.row() + 10
            item = self.table.item(row, 0)
            self.table.setCurrentItem(item)
            for item in matching_items:
                item.setSelected(True)

    def __init__(self, sattelites, timenow, save_to_json, place, selected_items, color, color_iter, load_from_json):
        super().__init__()

        self.setWindowTitle("Трекинг спутников на базе TLE данных")
        self.setMinimumSize(1280, 720)
        self.resize(630, 300)

        self.place = place
        self.save_to_json = save_to_json

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)

        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)

        self.selected_items = set(selected_items)
        self.color = dict(color)

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
        doubleSpinBox.setValue(place[1])
        doubleSpinBox.valueChanged.connect(lambda x: self.update_place(x, 1))

        doubleSpinBox_2 = QtWidgets.QDoubleSpinBox()
        doubleSpinBox_2.setGeometry(QtCore.QRect(230, 40, 161, 24))
        doubleSpinBox_2.setDecimals(6)
        doubleSpinBox_2.setMinimum(-180.0)
        doubleSpinBox_2.setMaximum(180.0)
        doubleSpinBox_2.setValue(place[0])
        doubleSpinBox_2.valueChanged.connect(lambda x: self.update_place(x, 0))

        doubleSpinBox_3 = QtWidgets.QDoubleSpinBox()
        doubleSpinBox_3.setGeometry(QtCore.QRect(230, 40, 161, 24))
        doubleSpinBox_3.setDecimals(3)
        doubleSpinBox_3.setValue(place[2])
        doubleSpinBox_3.valueChanged.connect(lambda x: self.update_place(x, 2))

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setRowCount(len(keys))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setHorizontalHeaderLabels(["Satellites"])

        # Расстановка спутников
        for i in range(len(keys)):
            item = QTableWidgetItem(keys[i])
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            if(keys[i] in self.selected_items):
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.table.setItem(i, 0, item)
        self.table.itemChanged.connect(self.message)


        tab_widget = QTabWidget()

        tab_schedule = TabSchedule(sattelites=sattelites, selected_items=self.selected_items)
        worldmap = TabWorldMap(sattelites=sattelites, place=self.place, selected_items=self.selected_items, color=self.color, save_to_json=save_to_json, color_iter=color_iter)
        tracking = TabTracking(sattelites=sattelites, timenow=timenow, place=self.place, selected_items=self.selected_items, color=self.color)
        settings = TabSettings(load_from_json=load_from_json, save_to_json=save_to_json, worldmap=worldmap, tracking=tracking)

        tab_widget.addTab(tracking, "Tracking")
        tab_widget.addTab(worldmap, "World Map")
        tab_widget.addTab(tab_schedule, "Schedule")
        tab_widget.addTab(settings, "Settings")

        update_button.clicked.connect(lambda x: (settings.save_settings(), tab_schedule.update_plot()))

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
        self.timer.timeout.connect(lambda : self.update_time(label_time, timenow))
        self.timer.start()


    def update_time(self, label_time: QLabel, timenow):
        label_time.setText(timenow().strftime("%d.%m.%Y %H:%M:%S"))

    def update_place(self, value: float, i: int):
        self.place[i] = value
        self.save_to_json(place = self.place)

class TabTracking(QWidget):
    def __init__(self, sattelites, timenow, place, selected_items, color):
        super().__init__()

        self.color = color
        self.selected_items = selected_items
        self.sattelites = sattelites
        self.timenow = timenow
        self.canvas = MplCanvas(self, width=90, height=90, dpi=100)
        #self.setCentralWidget(self.canvas)
        self.clear_all()
        self.show()

        self.old_selected_items = self.selected_items.copy()
        self.plots = {}
        self.fall_time = {}
        self.start_time = {}
        self.text = {}
        self.old_scatter = {}
        self.place = place
        self.old_place = place.copy()
        
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)
    def update_color(self):
        for i in self.selected_items:
            if(self.plots.get(i) != None):
                for j in self.plots.get(i):
                    j.remove()
                self.plots[i] = None
            observers = self.sattelites[i].get_next_observers(horizon = HORIZON, max_angle = MAX_ANGLE, delta_seconds = DELTA_SECONDS)
            self.fall_time[i] = observers[2]
            self.start_time[i] = observers[3]
            self.plots[i] = self.ax.plot(observers[0], observers[1], label=i, color=self.color.get(i))
            if(self.text.get(i) != None):
                self.text.get(i).remove()
                self.text[i] = None
            if(len(observers[0]) > 0):
                self.text[i] = self.ax.text(observers[0][0],observers[1][0],i, fontsize=12, backgroundcolor = (0.8,0.8,0.9,0.7))

    def update_plot(self):
        for i in self.selected_items:
            if (self.timenow() >= self.fall_time.get(i, self.timenow() - timedelta(days=1)) or self.old_place != self.place) and self.color.get(i) != None:
                if(self.plots.get(i) != None):
                    for j in self.plots.get(i):
                        j.remove()
                    self.plots[i] = None
                observers = self.sattelites[i].get_next_observers(horizon = HORIZON, max_angle = MAX_ANGLE, delta_seconds = DELTA_SECONDS)
                self.fall_time[i] = observers[2]
                self.start_time[i] = observers[3]
                self.plots[i] = self.ax.plot(observers[0], observers[1], label=i, color=self.color.get(i))
                if(self.text.get(i) != None):
                    self.text.get(i).remove()
                    self.text[i] = None
                if(len(observers[0]) > 0):
                    self.text[i] = self.ax.text(observers[0][0],observers[1][0],i, fontsize=12, backgroundcolor = (0.8,0.8,0.9,0.7))
            
            if(self.start_time.get(i, self.timenow() + timedelta(days=1)) <= self.timenow() and self.timenow() <= self.fall_time.get(i, self.timenow() - timedelta(days=1))):
                k = self.sattelites.get(i).get_observer()
                if(self.old_scatter.get(i) != None):
                    self.old_scatter.get(i).remove()
                    self.old_scatter[i] = None
                self.old_scatter[i] = self.ax.scatter(k[0], k[1], color = self.color.get(i), alpha=0.5)

                if(self.text.get(i) != None):
                    self.text.get(i).remove()
                    self.text[i] = None
                self.text[i] = self.ax.text(k[0], k[1], i, fontsize=12)
            elif(self.old_scatter.get(i) != None):
                self.old_scatter.get(i).remove()
                self.old_scatter[i] = None
                
        
        if self.old_place != self.place:
            self.old_place = self.place.copy()
        

        for i in self.old_selected_items - self.selected_items:
            for j in self.plots.get(i):
                j.remove()
            self.fall_time[i] = self.timenow()
            self.plots[i] = None
            if(self.text.get(i) != None):
                self.text.get(i).remove()
                self.text[i] = None
            if(self.old_scatter.get(i) != None):
                self.old_scatter.get(i).remove()
                self.old_scatter[i] = None

        self.old_selected_items = self.selected_items.copy()

        self.ax.set_rmax(0)
        self.ax.set_rmin(90)
        self.canvas.draw()

    def clear_all(self):
        self.canvas.figure.clear()
        self.ax = self.canvas.figure.add_subplot(111, projection='polar')
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)
        self.ax.set_rmax(0)
        self.ax.set_rmin(90)
        self.ax.set_rticks([0, 15, 30, 45, 60, 75, 90])  # Пример значений на радиусе
        self.ax.grid(True)

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        fig = plt.figure(figsize=(width, height), edgecolor='w')
        super(MplCanvas, self).__init__(fig)

class TabWorldMap(QWidget):
    def __init__(self, sattelites, place, selected_items, color, save_to_json, color_iter):
        super().__init__()
        vbox = QVBoxLayout()

        self.color = color
        self.selected_items = selected_items
        self.save_to_json = save_to_json

        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.clear_all()

        self.sattelites = sattelites

        self.old_selected_items = self.selected_items.copy()

        self.old_scatter = {}
        self.orbit_number = {}
        self.plotes = {}
        self.text = {}
        self.color_iter = color_iter

        self.place_pos = place
        self.old_place_pos = place.copy()
        self.place = self.m.scatter(self.place_pos[0], self.place_pos[1], latlon=True, color =(1,0.5,0.5), alpha=0.5)
        self.text_place = self.plt.text(self.place_pos[0]+6, self.place_pos[1]+6, "Your Place", fontsize=8, backgroundcolor = (1,1,1,0.7))

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
            llcrnrlon=-180, urcrnrlon=180, ax=self.canvas.figure.gca())
        self.plt = self.canvas.figure.gca()
        draw_map(self.m)
    
    def update_color(self):
        self.color_iter = 0
        for i in self.color.keys():
            self.color[i] = rainbow(self.color_iter, COLOR_VAL, COLOR_BRIGHTNESS, COLOR_UNBRIGHTNESS)
            self.color_iter += 1
            self.save_to_json(color = self.color, color_iter = self.color_iter)
            if(self.color_iter >= COLOR_VAL*(1/COLOR_UNBRIGHTNESS)*(1/(COLOR_BRIGHTNESS-COLOR_UNBRIGHTNESS))):
                self.color_iter = 0
            col = self.color.get(i)

            self.orbit_number[i] = self.sattelites[i].get_orbit_number()
            l = self.sattelites[i].get_while_loc(deltaseconds = 10)
            l_old = rasdel(l)
            if self.plotes.get(i) != None:
                for j in self.plotes.get(i):
                    j.remove()
            self.plotes[i] = []

            for o in l_old:
                j,  = self.m.plot(o[0], o[1], color = col)
                self.plotes[i].append(j)

            self.update_plot()

    
    def update_plot(self):
        #self.clear()
        update_place = False
        if(self.place_pos != self.old_place_pos):
            self.place.remove()
            self.text_place.remove()

            self.place = self.m.scatter(self.place_pos[0], self.place_pos[1], latlon=True, color =(1,0.5,0.5), alpha=0.5)
            self.text_place = self.plt.text(self.place_pos[0]+6, self.place_pos[1]+6, "Your Place", fontsize=8, backgroundcolor = (1,1,1,0.7))
            
            self.old_place_pos = self.place_pos.copy()

            update_place = True
        for i in self.selected_items:
            if(self.color.get(i) == None):
                self.color[i] = rainbow(self.color_iter, COLOR_VAL, COLOR_BRIGHTNESS, COLOR_UNBRIGHTNESS)
                self.color_iter += 1
                self.save_to_json(color = self.color, color_iter = self.color_iter)
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
                    j,  = self.m.plot(o[0], o[1], color = col)
                    self.plotes[i].append(j)

            if(self.old_scatter.get(i) != None):
                self.old_scatter.get(i).remove()
                self.old_scatter[i] = None
            k = self.sattelites.get(i).get_location()
            self.old_scatter[i] = self.m.scatter(k[0], k[1], latlon=True, color = col, alpha=0.5)
            if(self.text.get(i) != None):
                self.text.get(i).remove()
                self.text[i] = None
            x, y = self.m(k[0], k[1])
            self.text[i] = self.plt.text(x+6, y+6, i, fontsize=12, backgroundcolor = (0.8,0.8,0.9,0.7))

            if(update_place):
                self.sattelites[i].update_place(self.place_pos)

        for i in self.old_selected_items - self.selected_items:
            self.old_scatter.get(i).remove()
            for j in self.plotes.get(i):
                j.remove()
            self.plotes[i] = []
            self.old_scatter[i] = None
            self.orbit_number[i] = None
            self.text.get(i).remove()
            self.text[i] = None
        
        for i in self.selected_items - self.old_selected_items:
            self.sattelites[i].update_place(self.place_pos)

        self.old_selected_items = self.selected_items.copy()

        self.canvas.draw()

class TabSchedule(QWidget):
    def __init__(self, sattelites, selected_items):
        super().__init__()

        self.sattelites = sattelites
        self.selected_items = selected_items

        vbox = QVBoxLayout()

        label = QLabel("Click Update button to update the table.")

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(len(self.selected_items))

        # Заполнение таблицы при запуске
        self.update_plot()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.setHorizontalHeaderLabels(["Name", "Time of start", "Time of stop", "Apogee"])

        vbox.addWidget(label)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def update_plot(self):
        list_of_selected_items = list(self.selected_items)
        count_of_list = len(list_of_selected_items)
        all_passes = []
        for i in range(count_of_list):
            name = list_of_selected_items[i]

            next_passes = self.sattelites[name].get_next_passes(max_angle = MAX_ANGLE)
            for j in range(len(next_passes)):
                next_passes[j] = (name, next_passes[j][0], next_passes[j][1], next_passes[j][2])
            all_passes += next_passes
        all_passes.sort(key=lambda x: x[1].timestamp())
        self.table.setRowCount(len(all_passes))
        for i in range(len(all_passes)):
            name = all_passes[i][0]
            name_item = QTableWidgetItem(name)
            self.table.setItem(i, 0, name_item)

            time_of_start = all_passes[i][1]
            time_of_start_item = QTableWidgetItem(time_of_start.strftime("%d.%m.%Y %H:%M:%S"))
            self.table.setItem(i, 1, time_of_start_item)

            time_of_end = all_passes[i][2]
            time_of_end_item = QTableWidgetItem(time_of_end.strftime("%d.%m.%Y %H:%M:%S"))
            self.table.setItem(i, 2, time_of_end_item)
            
            apogee = self.sattelites[name].get_observer(time=all_passes[i][3])[1]
            apogee_item = QTableWidgetItem(str(round(apogee, 1)))
            self.table.setItem(i, 3, apogee_item)

class TabSettings(QWidget):
    def __init__(self, load_from_json, save_to_json, worldmap, tracking):
        super().__init__()

        self.save_to_json = save_to_json
        self.load_from_json = load_from_json
        self.functions_update = []
        self.functions_value = []
        self.worldmap = worldmap
        self.tracking = tracking
        vbox = QVBoxLayout()

        label = QLabel("Click Update button to save and update settings.")
        vbox.addWidget(label)

        hbox_1 = QHBoxLayout()
        self.spinBox = QtWidgets.QSpinBox()
        self.label = QtWidgets.QLabel()
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(20)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setText("COLOR_VAL")
        hbox_1.addWidget(self.spinBox)
        self.functions_update.append(lambda x: self.spinBox.setValue(x))
        self.functions_value.append(lambda : self.spinBox.value())
        hbox_1.addWidget(self.label)
        vbox.addLayout(hbox_1)

        hbox_2 = QHBoxLayout()
        self.plainTextEdit = QtWidgets.QPlainTextEdit()
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_2.setText("TLE_URLS\n\n\n ")
        hbox_2.addWidget(self.plainTextEdit)
        self.functions_value.append(lambda : self.plainTextEdit.toPlainText().split(';\n'))
        self.functions_update.append(lambda x: self.plainTextEdit.setPlainText(';\n'.join(x)))
        hbox_2.addWidget(self.label_2)
        vbox.addLayout(hbox_2)  

        hbox_3 = QHBoxLayout()
        self.timeEdit = QtWidgets.QSpinBox()
        self.timeEdit.setMaximum(24*7)
        self.timeEdit.setMinimum(1)
        self.timeEdit.setSingleStep(12)
        self.label_3 = QtWidgets.QLabel()
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setText("DELTA_TLE_HOURS")
        hbox_3.addWidget(self.timeEdit)
        self.functions_value.append(lambda : self.timeEdit.value())
        self.functions_update.append(lambda x: self.timeEdit.setValue(x))
        hbox_3.addWidget(self.label_3)
        vbox.addLayout(hbox_3)  

        hbox_4 = QHBoxLayout()
        self.label_4 = QtWidgets.QLabel()
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.timeEdit_2 = QtWidgets.QSpinBox()
        self.timeEdit_2.setMaximum(24*7)
        self.timeEdit_2.setMinimum(1)
        self.timeEdit_2.setSingleStep(12)
        self.label_4.setText("LENGHT_PASSES")
        hbox_4.addWidget(self.timeEdit_2)
        self.functions_value.append(lambda : self.timeEdit_2.value())
        self.functions_update.append(lambda x: self.timeEdit_2.setValue(x))
        hbox_4.addWidget(self.label_4)
        vbox.addLayout(hbox_4)  

        hbox_5 = QHBoxLayout()
        self.label_5 = QtWidgets.QLabel()
        self.label_5.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox.setMaximum(1)
        self.doubleSpinBox.setMinimum(0)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setSingleStep(0.1)
        self.label_5.setText("COLOR_BRIGHTNESS")
        hbox_5.addWidget(self.doubleSpinBox)
        self.functions_value.append(lambda : self.doubleSpinBox.value())
        self.functions_update.append(lambda x: self.doubleSpinBox.setValue(x))
        hbox_5.addWidget(self.label_5)
        vbox.addLayout(hbox_5)  

        hbox_6 = QHBoxLayout()
        self.label_6 = QtWidgets.QLabel()
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_2.setMaximum(1)
        self.doubleSpinBox_2.setMinimum(0)
        self.doubleSpinBox_2.setDecimals(3)
        self.doubleSpinBox_2.setSingleStep(0.1)
        self.label_6.setText("COLOR_UNBRIGHTNESS")
        hbox_6.addWidget(self.doubleSpinBox_2)
        self.functions_value.append(lambda : self.doubleSpinBox_2.value())
        self.functions_update.append(lambda x: self.doubleSpinBox_2.setValue(x))
        hbox_6.addWidget(self.label_6)
        vbox.addLayout(hbox_6)  

        hbox_7 = QHBoxLayout()
        self.label_7 = QtWidgets.QLabel()
        self.label_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_3 = QtWidgets.QSpinBox()
        self.spinBox_3.setMaximum(360)
        self.spinBox_3.setMinimum(0)
        self.spinBox_3.setSingleStep(10)
        self.label_7.setText("COVERAGE_LON")
        hbox_7.addWidget(self.spinBox_3)
        self.functions_value.append(lambda : self.spinBox_3.value())
        self.functions_update.append(lambda x: self.spinBox_3.setValue(x))
        hbox_7.addWidget(self.label_7)
        vbox.addLayout(hbox_7)  

        hbox_8 = QHBoxLayout()
        self.label_8 = QtWidgets.QLabel()
        self.label_8.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_2 = QtWidgets.QSpinBox()
        self.spinBox_2.setMaximum(90)
        self.spinBox_2.setMinimum(0)
        self.spinBox_2.setSingleStep(5)
        self.label_8.setText("MAX_ANGLE")
        hbox_8.addWidget(self.spinBox_2)
        self.functions_value.append(lambda : self.spinBox_2.value())
        self.functions_update.append(lambda x: self.spinBox_2.setValue(x))
        hbox_8.addWidget(self.label_8)
        vbox.addLayout(hbox_8)  

        hbox_9 = QHBoxLayout()
        self.label_9 = QtWidgets.QLabel()
        self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_4 = QtWidgets.QSpinBox()
        self.spinBox_4.setMaximum(1000)
        self.spinBox_4.setMinimum(0)
        self.spinBox_4.setSingleStep(10)
        self.label_9.setText("SPEED")
        hbox_9.addWidget(self.spinBox_4)
        self.functions_value.append(lambda : self.spinBox_4.value())
        self.functions_update.append(lambda x: self.spinBox_4.setValue(x))
        hbox_9.addWidget(self.label_9)
        vbox.addLayout(hbox_9)  

        self.update_settings()

        self.setLayout(vbox)

    def save_settings(self):
        j = {}
        for i in range(len(self.old_settings)):
            if(self.old_settings[i] != self.functions_value[i]()):
                j[self.names[i]] = self.functions_value[i]()


        self.save_to_json(**j)
        self.update_settings()
        for i in j.keys():
            match i:
                case "COLOR_VAL" | "COLOR_BRIGHTNESS" | "COLOR_UNBRIGHTNESS":
                    self.worldmap.update_color()
                    self.tracking.update_color()
                case "COVERAGE_LON":
                    self.worldmap.update_color()
                case "MAX_ANGLE":
                    self.tracking.update_color()



    def update_settings(self):
        self.names = ["COLOR_VAL", "TLE_URLS", "DELTA_TLE_HOURS", "LENGHT_PASSES", "COLOR_BRIGHTNESS", "COLOR_UNBRIGHTNESS", "COVERAGE_LON", "MAX_ANGLE", "SPEED"]
        self.old_settings = self.load_from_json("COLOR_VAL", "TLE_URLS", "DELTA_TLE_HOURS", "LENGHT_PASSES", "COLOR_BRIGHTNESS", "COLOR_UNBRIGHTNESS", "COVERAGE_LON", "MAX_ANGLE", "SPEED")

        for i in range(len(self.old_settings)):
            self.functions_update[i](self.old_settings[i])






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

def window(sattelite, timenow, load_from_json, save_to_json, place, selected_items, color, color_iter):
    save_to_json = save_to_json
    app = QApplication(sys.argv)
    window = MainWindow(sattelites=sattelite, timenow=timenow, save_to_json=save_to_json, place = place, selected_items = selected_items, color=color, color_iter=color_iter, load_from_json=load_from_json)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()