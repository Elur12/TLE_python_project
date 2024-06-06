import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')

from itertools import chain

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import satelite


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

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        fig = plt.figure(figsize=(width, height), edgecolor='w')
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()

        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.setCentralWidget(self.canvas)

        self.clear_all()

        self.get_latlon = kwargs["func_get_latlon"]
        self.get_orbit_number = kwargs["func_get_orbit_number"]
        self.orbit_number = None
        self.quotes = []
        self.update_plot()

        #self.func = func
        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def clear_all(self):
        self.canvas.figure.clear()
        self.m = Basemap(projection='cyl', resolution=None,
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180, )
        draw_map(self.m)

    def update_plot(self):
        #self.clear()
        if(self.orbit_number != self.get_orbit_number()):
            self.orbit_number = self.get_orbit_number()
            l = self.get_latlon()
            if len(self.quotes) > 0:
                for q in self.quotes:
                    q.remove()
                self.quotes.clear()
            for i in range(len(l) - 1):
                self.quotes.append(self.m.quiver(x = l[i][0], y= l[i][1], u=l[i+1][0] - l[i][0], v=l[i+1][1] - l[i][1], scale = 500, color = (1,0,0)))
        
        self.canvas.draw()
        

def main(func, func2):
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(func_get_latlon = func, func_get_orbit_number = func2)
    app.exec_()

if __name__ == "__main__":
    main()