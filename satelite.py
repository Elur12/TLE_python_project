import pyorbital as por
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
from datetime import UTC
import requests
import os
from dataclasses import dataclass
import pickle as pk
import interface.window as win

'''
start_time = datetime.utcnow()
#FOR PYTHON <3.12
def timenow(start_time: datetime = datetime.utcnow(), use_speed: bool = False):
    if(use_speed):
        return start_time + (datetime.utcnow() - start_time) * SPEED
    else:
        return datetime.utcnow()
'''

#FOR PYTHON3.12
start_time = datetime.now(UTC)
def timenow(start_time: datetime = start_time, use_speed: bool = False):
    if(use_speed):
        return start_time + (datetime.now(UTC) - start_time) * SPEED
    else:
        return datetime.now(UTC)
    

def save_to_pk(**kwargs): 
    global start_time
    data = {}
    create_folder(os.path.dirname(os.path.abspath(__file__)), 'data')
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.pk', 'rb') as file:
            data = pk.load(file)
    except:
        print("creating data file")
    with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.pk', 'wb') as file:
        up = False
        for i in kwargs.keys():
            data[i] = kwargs[i]
            if i in ('SPEED', 'TLE_URLS', 'DELTA_TLE_HOURS', 'LENGHT_PASSES', 'COLOR_BRIGHTNESS', \
                        'COLOR_UNBRIGHTNESS', 'COLOR_VAL', 'COVERAGE_LON', 'MAX_ANGLE', \
                            'HORIZON', 'DELTA_SECONDS'):
                up = True
        pk.dump(data, file)
    for i in kwargs.keys():
        match i:
            case "SPEED":
                start_time = timenow()
                for i in satelites.keys():
                    satelites[i].start_time = timenow()
            case "DELTA_TLE_HOURS":
                update_tle(TLE_URLS)
    if(up):
        update_settings()

def load_from_pk(*args):
    data = {}
    set_args = set(args)
    result = [0]*len(args)
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.pk', 'rb') as file:
            data = pk.load(file)
            set_args = set(data.keys()) & set_args
            for i in range(len(args)):
                if(args[i] in set_args):
                    result[i]=data[args[i]]
    except:
        save_to_pk(color_iter = 0, color = {}, selected_items = (), place = [0,0,0], SPEED = SPEED, TLE_URLS = TLE_URLS, DELTA_TLE_HOURS = DELTA_TLE_HOURS, LENGHT_PASSES = LENGHT_PASSES, COLOR_BRIGHTNESS = win.COLOR_BRIGHTNESS, COLOR_UNBRIGHTNESS = win.COLOR_UNBRIGHTNESS, COLOR_VAL = win.COLOR_VAL, COVERAGE_LON = win.COVERAGE_LON, MAX_ANGLE = win.MAX_ANGLE, HORIZON = win.HORIZON, DELTA_SECONDS = win.DELTA_SECONDS)
        print("No file")
        result = load_from_pk(*args)
    return result



SPEED = 1

TLE_URLS = ['http://www.celestrak.com/NORAD/elements/active.txt',
            'http://celestrak.com/NORAD/elements/weather.txt',
            'http://celestrak.com/NORAD/elements/resource.txt',
            'https://www.celestrak.com/NORAD/elements/cubesat.txt',
            'http://celestrak.com/NORAD/elements/stations.txt',
            'https://www.celestrak.com/NORAD/elements/sarsat.txt',
            'https://www.celestrak.com/NORAD/elements/noaa.txt',
            'https://www.celestrak.com/NORAD/elements/amateur.txt',
            'https://www.celestrak.com/NORAD/elements/engineering.txt']

DELTA_TLE_HOURS = 24
LENGHT_PASSES = 48

satelite_line = {}

satelites = {}

update_date = timenow() - timedelta(hours=DELTA_TLE_HOURS + 1)


@dataclass
class place:
    lon: float = 0
    lat: float = 0
    alt: float = 0 #On km

def TLE(func):
    def wrapper(*args, **kwargs):
        global update_date
        if(timenow() - timedelta(hours=DELTA_TLE_HOURS) >= update_date):
            update_date = update_tle(TLE_URLS)
            for i in satelites.keys():
                satelites[i].update()
        return func(*args, **kwargs)
    return wrapper

def csv_info(func):
    def wrapper(*args, **kwargs):
        g, n = func(*args, **kwargs)
        creat_add_info(g, n)
        return g, n
    return wrapper

class Satelite():
    my_place: place
    orb: Orbital
    name: str
    def __init__(self, name: str, place: place) -> None:
        self.my_place = place
        self.name = name
        self.start_time = timenow()
        self.orb = Orbital(name, line1=satelite_line[name][0], line2=satelite_line[name][1])

    @TLE
    def get_location(self):
        return self.orb.get_lonlatalt(timenow(self.start_time, use_speed=True))
    
    @TLE
    def get_while_loc(self, deltaseconds: float = 10):
        i = 0
        dt = timenow(self.start_time, use_speed=True)
        lonlatalt = [[],[]]
        orbit_num = self.orb.get_orbit_number(timenow(self.start_time, use_speed = True))

        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt + timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt_h = self.orb.get_lonlatalt(dt)
            lonlatalt[0].append(lonlatalt_h[0])
            lonlatalt[1].append(lonlatalt_h[1])

        dt = timenow(self.start_time, use_speed=True)

        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt - timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt_h = self.orb.get_lonlatalt(dt)
            lonlatalt[0] = [lonlatalt_h[0]] + lonlatalt[0]
            lonlatalt[1] = [lonlatalt_h[1]] + lonlatalt[1]

        return lonlatalt

    @TLE
    def get_orbit_number(self):
        return self.orb.get_orbit_number(timenow(self.start_time, use_speed=True))

    @TLE
    def get_observer(self, time: datetime = None):
        if(time == None):
            return self.observer(timenow(self.start_time, use_speed=True))
        else:
            return self.observer(time)

    def observer(self, time: datetime):
        observer = self.orb.get_observer_look(time, self.my_place.lon, self.my_place.lat, self.my_place.alt)
        return ((observer[0]/360) * 2 * 3.14, observer[1])

    @TLE
    def get_next_observers(self, horizon = 0, max_angle = 60, delta_seconds = 0.5):
        passe, name = self.get_next_passes(horizon=horizon, max_angle=max_angle)
        observers = [[],[], timenow(self.start_time, use_speed=True), timenow(self.start_time, use_speed=True)]
        if(len(passe) > 0):
            passe = passe[0]
            now_time = passe[0]
            observers[2] = passe[1]
            observers[3] = passe[0]
            while now_time < passe[1]:
                observer = self.orb.get_observer_look(now_time, self.my_place.lon, self.my_place.lat, self.my_place.alt)
                observers[0].append((observer[0]/360) * 2 * 3.14)
                observers[1].append(observer[1])
                now_time = now_time + timedelta(seconds=delta_seconds)

        return observers

    @TLE
    @csv_info
    def get_next_passes(self, horizon = 0, max_angle = 30):
        passes = self.orb.get_next_passes(timenow(self.start_time, use_speed=True), LENGHT_PASSES, self.my_place.lon, self.my_place.lat, self.my_place.alt, horizon=horizon)
        i = 0
        while i < len(passes):
            passes[i] = list(passes[i])
            passes[i].append(self.orb.get_observer_look(passes[i][2], self.my_place.lon, self.my_place.lat, self.my_place.alt)[1])
            if(self.orb.get_observer_look(passes[i][2], self.my_place.lon, self.my_place.lat, self.my_place.alt)[1] < max_angle):
                passes.pop(i)
            else:
                i += 1

        return passes, self.name

    @TLE
    def get_positions(self):
        return self.orb.get_position(self.timenow(self.start_time, use_speed=True), normalize=False)

    def update_place(self, my_place):
        if(type(my_place) != place):
            self.my_place = place(my_place[0],my_place[1],my_place[2])
        else:
            self.my_place = my_place

    def update(self):
        self.orb = Orbital(self.name, line1=satelite_line[self.name][0], line2=satelite_line[self.name][1])

def creat_add_info(inf,name):
    create_folder(os.path.dirname(os.path.abspath(__file__)), 'data')
    lines = []
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.csv', 'r') as file:
            lines = file.readlines().copy()
    except:
        pass
    with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.csv', 'w') as file:
        op = []
        for j in inf:
            add = True
            for i in lines:
                stri = i.split(";")
                if(stri[0] == name):
                    date_start = datetime.strptime(stri[1], "%c").replace(tzinfo=UTC)

                    if(date_start - timedelta(minutes=5) < j[0] or j[0] < date_start + timedelta(minutes=5)):
                        add = False
            if(add):
                op.append(j.copy())
        for i in range(len(op)):
            l = [0]*4
            l[0] = op[i][0].strftime("%c")
            l[1] = op[i][1].strftime("%c")
            l[2] = op[i][2].strftime("%c")
            l[3] = str(op[i][3])
            lines.append(name + ';' + ';'.join(l) + '\n')
        for i in lines:
            if(i != '\n'):
                file.write(i)
        

def update_tle(urls, all_update: bool = False) -> datetime:
    update = timenow() - timedelta(hours=DELTA_TLE_HOURS + 1)
    create_folder(os.path.dirname(os.path.abspath(__file__)), 'tle')
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/tle'):  
        for filename in files:

            old_tle_date = datetime.strptime(filename, "tle_%d_%m_%Y-%H:%M:%S.txt").replace(tzinfo=UTC)
            
            if(old_tle_date > update):
                update = old_tle_date
    
    if(timenow() - timedelta(hours=DELTA_TLE_HOURS) >= update or all_update):
        update = timenow()
        with open(os.path.dirname(os.path.abspath(__file__)) + '/tle/' + update.strftime("tle_%d_%m_%Y-%H:%M:%S.txt"), 'w') as file:
            for url in urls:
                response = requests.get(url)
                if(response.status_code == 200):
                    file.write(response.text)
    
    with open(os.path.dirname(os.path.abspath(__file__)) + '/tle/' + update.strftime("tle_%d_%m_%Y-%H:%M:%S.txt"), 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            name = lines[i].strip()
            line1 = lines[i+1].strip()
            line2 = lines[i+2].strip()
            satelite_line.update({name : (line1, line2)})
    
    return update

def create_folder(workspace, folder):
    path = os.path.join(workspace, folder)
    if not os.path.exists(path):
        os.makedirs(path)
        print("create folder with path {0}".format(path))
    else:
        print("folder exists {0}".format(path))

def update_settings():
    global SPEED, TLE_URLS, DELTA_TLE_HOURS, LENGHT_PASSES
    SPEED, TLE_URLS, DELTA_TLE_HOURS, LENGHT_PASSES, win.COLOR_BRIGHTNESS, \
        win.COLOR_UNBRIGHTNESS, win.COLOR_VAL, win.COVERAGE_LON, win.MAX_ANGLE, \
            win.HORIZON, win.DELTA_SECONDS = load_from_pk('SPEED', 'TLE_URLS', 'DELTA_TLE_HOURS', 'LENGHT_PASSES', 'COLOR_BRIGHTNESS', \
                'COLOR_UNBRIGHTNESS', 'COLOR_VAL', 'COVERAGE_LON', 'MAX_ANGLE', \
                    'HORIZON', 'DELTA_SECONDS')

if __name__ == "__main__":
    update_settings()
    update_date = update_tle(TLE_URLS)
    my_place = load_from_pk('place')[0]
    for i in satelite_line.keys():
        try:
            satelites.update({i:Satelite(i, place(my_place[0], my_place[1], my_place[2]))})
        except:
            print("Satellite: ", i, ", doesn't work")
    win.window(satelites, lambda : timenow(use_speed=True), load_from_pk, save_to_pk, load_from_pk('place')[0], load_from_pk('selected_items')[0], load_from_pk('color')[0], load_from_pk('color_iter')[0])