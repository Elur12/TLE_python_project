import pyorbital as por
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
from datetime import UTC
import requests
import os
from dataclasses import dataclass
import pickle as json
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
    

def save_to_json(**kwargs):
    data = {}
    create_folder(os.path.dirname(os.path.abspath(__file__)), 'data')
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.json', 'rb') as file:
            data = json.load(file)
    except:
        print("creating data file")
    with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.json', 'wb') as file:
        for i in kwargs.keys():
            data[i] = kwargs[i]
        json.dump(data, file)

def load_from_json(*args):
    data = {}
    set_args = set(args)
    result = [0]*len(args)
    try:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/data/' + 'data.json', 'rb') as file:
            data = json.load(file)
            set_args = set(data.keys()) & set_args
            for i in range(len(args)):
                if(args[i] in set_args):
                    result[i]=data[args[i]]
    except:
        save_to_json(color_iter = 0, color = {}, selected_items = (), place = [0,0,0], SPEED = SPEED, TLE_URLS = TLE_URLS, DELTA_TLE_HOURS = DELTA_TLE_HOURS, LENGHT_PASSES = LENGHT_PASSES, COLOR_BRIGHTNESS = win.COLOR_BRIGHTNESS, COLOR_UNBRIGHTNESS = win.COLOR_UNBRIGHTNESS, COLOR_VAL = win.COLOR_VAL, COVERAGE_LON = win.COVERAGE_LON, MAX_ANGLE = win.MAX_ANGLE, HORIZON = win.HORIZON, DELTA_SECONDS = win.DELTA_SECONDS)
        print("No file")
        result = load_from_json(*args)
    return result


SPEED = 100

TLE_URLS = ('http://www.celestrak.com/NORAD/elements/active.txt',
            'http://celestrak.com/NORAD/elements/weather.txt',
            'http://celestrak.com/NORAD/elements/resource.txt',
            'https://www.celestrak.com/NORAD/elements/cubesat.txt',
            'http://celestrak.com/NORAD/elements/stations.txt',
            'https://www.celestrak.com/NORAD/elements/sarsat.txt',
            'https://www.celestrak.com/NORAD/elements/noaa.txt',
            'https://www.celestrak.com/NORAD/elements/amateur.txt',
            'https://www.celestrak.com/NORAD/elements/engineering.txt')

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
        passe = self.get_next_passes(horizon=horizon, max_angle=max_angle)
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
    def get_next_passes(self, horizon = 0, max_angle = 30):
        passes = self.orb.get_next_passes(timenow(self.start_time, use_speed=True), LENGHT_PASSES, self.my_place.lon, self.my_place.lat, self.my_place.alt, horizon=horizon)
        i = 0
        while i < len(passes):
            if(self.orb.get_observer_look(passes[i][2], self.my_place.lon, self.my_place.lat, self.my_place.alt)[1] < max_angle):
                passes.pop(i)
            else:
                i += 1

        return passes

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

def update_tle(urls) -> datetime:
    update = timenow() - timedelta(hours=DELTA_TLE_HOURS + 1)
    create_folder(os.path.dirname(os.path.abspath(__file__)), 'tle')
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/tle'):  
        for filename in files:

            old_tle_date = datetime.strptime(filename, "tle_%d_%m_%Y-%H:%M:%S.txt").replace(tzinfo=UTC)
            
            if(old_tle_date > update):
                update = old_tle_date
    
    if(timenow() - timedelta(hours=DELTA_TLE_HOURS) >= update):
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

if __name__ == "__main__":
    update_date = update_tle(TLE_URLS)
    my_place = load_from_json('place')[0]
    for i in satelite_line.keys():
        try:
            satelites.update({i:Satelite(i, place(my_place[0], my_place[1], my_place[2]))})
        except:
            print("Satellite: ", i, ", doesn't work")
    win.window(satelites, lambda : timenow(use_speed=True), save_to_json, load_from_json('place')[0], load_from_json('selected_items')[0], load_from_json('color')[0], load_from_json('color_iter')[0])