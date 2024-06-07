import pyorbital as por
from pyorbital.orbital import Orbital
from datetime import datetime, UTC, timedelta
import requests
import os
from dataclasses import dataclass

import numpy as np

import interface.window as win

#orb = 

TLE_URLS = ('http://www.celestrak.com/NORAD/elements/active.txt',
            'http://celestrak.com/NORAD/elements/weather.txt',
            'http://celestrak.com/NORAD/elements/resource.txt',
            'https://www.celestrak.com/NORAD/elements/cubesat.txt',
            'http://celestrak.com/NORAD/elements/stations.txt',
            'https://www.celestrak.com/NORAD/elements/sarsat.txt',
            'https://www.celestrak.com/NORAD/elements/noaa.txt',
            'https://www.celestrak.com/NORAD/elements/amateur.txt',
            'https://www.celestrak.com/NORAD/elements/engineering.txt')

delta_tle_hours = 24

satelite_line = {}

satelites = {}

update_date = datetime.now(UTC) - timedelta(hours=delta_tle_hours + 1)

@dataclass
class place:
    lat: float = 0
    lon: float = 0
    alt: float = 0 #On km

def TLE(func):
    def wrapper(*args, **kwargs):
        global update_date
        if(datetime.now(UTC) - timedelta(hours=delta_tle_hours) >= update_date):
            update_date = update_tle(TLE_URLS)
            for i in satelites.keys():
                satelites[i].update()
        return func(*args, **kwargs)
    return wrapper

class Satelite():
    my_place: place
    orb: Orbital
    name: str
    speed: float
    def __init__(self, name: str, place: place, speed: float) -> None:
        self.my_place = place
        self.name = name
        self.speed = speed
        self.start_time = datetime.now(UTC)
        self.orb = Orbital(name, line1=satelite_line[name][0], line2=satelite_line[name][1])

    def timenow(self):
        return self.start_time + (datetime.now(UTC) - self.start_time) * self.speed

    @TLE
    def get_location(self):
        return self.orb.get_lonlatalt(self.timenow())
    
    @TLE
    def get_while_loc(self, deltaseconds: float = 10):
        i = 0
        dt = self.timenow()
        lonlatalt = [[],[]]
        orbit_num = self.orb.get_orbit_number(self.timenow())

        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt + timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt[0].append(self.orb.get_lonlatalt(dt)[0])
            lonlatalt[1].append(self.orb.get_lonlatalt(dt)[1])

        dt = self.timenow()

        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt - timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt[0] = [self.orb.get_lonlatalt(dt)[0]] + lonlatalt[0]
            lonlatalt[1] = [self.orb.get_lonlatalt(dt)[1]] + lonlatalt[1]

        return lonlatalt

    @TLE
    def get_orbit_number(self):
        return self.orb.get_orbit_number(self.timenow())

    @TLE
    def get_observer(self):
        return self.orb.get_observer_look(self.timenow(), self.my_place.lon, self.my_place.lat, self.my_place.alt)
    
    #@TLE
    #def get_positions(self):
    #    return self.orb.get_position(self.timenow(), normalize=False)

    def update_place(self, place: place):
        self.my_place = place

    def update(self):
        self.orb = Orbital(self.name, line1=satelite_line[self.name][0], line2=satelite_line[self.name][1])

def update_tle(urls) -> datetime:
    update = datetime.now(UTC) - timedelta(hours=delta_tle_hours + 1)
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/tle'):  
        for filename in files:

            old_tle_date = datetime.strptime(filename, "tle_%d_%m_%Y-%H:%M:%S.txt").replace(tzinfo=UTC)
            
            if(old_tle_date > update):
                update = old_tle_date
    
    if(datetime.now(UTC) - timedelta(hours=delta_tle_hours) >= update):
        update = datetime.now(UTC)
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

if __name__ == "__main__":
    update_date = update_tle(TLE_URLS)
    for i in satelite_line.keys():
        try:
            satelites.update({i:Satelite(i, place(55, 37, 0.1), 100)})
        except:
            print("Sattelite: ", i, ", doesn't work")

    win.window(satelites)