import pyorbital as por
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
import requests
import os
from dataclasses import dataclass

import numpy as np

import windows

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

satelites = []

update_date = datetime.utcnow() - timedelta(hours=delta_tle_hours + 1)

@dataclass
class place:
    lat: float = 0
    lon: float = 0
    alt: float = 0 #On km

def TLE(func):
    def wrapper(*args, **kwargs):
        global update_date
        if(datetime.utcnow() - timedelta(hours=delta_tle_hours) >= update_date):
            update_date = update_tle(TLE_URLS)
        return func(*args, **kwargs)
    return wrapper

class Satelite():
    my_place: place
    orb: Orbital
    name: str
    def __init__(self, name: str, place: place) -> None:
        self.my_place = place
        self.name = name
        self.orb = Orbital(name, line1=satelite_line[name][0], line2=satelite_line[name][1])

    @TLE
    def get_location(self):
        return self.orb.get_lonlatalt(datetime.utcnow())
    
    @TLE
    def get_while_loc(self, deltaseconds = 10):
        i = 0
        dt = datetime.utcnow()
        lonlatalt = []
        orbit_num = self.orb.get_orbit_number(datetime.utcnow())
        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt + timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt.append(self.orb.get_lonlatalt(dt))
        dt = datetime.utcnow()
        while i < 1000 and self.orb.get_orbit_number(dt) == orbit_num:
            dt = dt - timedelta(seconds=deltaseconds)
            i += 1
            lonlatalt = [self.orb.get_lonlatalt(dt)] + lonlatalt

        return lonlatalt

    @TLE
    def get_orbit_number(self):
        return self.orb.get_orbit_number(datetime.utcnow())

    @TLE
    def get_observer(self):
        return self.orb.get_observer_look(datetime.utcnow(), self.my_place.lon, self.my_place.lat, self.my_place.alt)
    
    #@TLE
    #def get_positions(self):
    #    return self.orb.get_position(datetime.utcnow(), normalize=False)

    def update(self):
        self.orb = Orbital(self.name, line1=satelite_line[self.name][0], line2=satelite_line[self.name][1])





def update_tle(urls) -> datetime:
    update = datetime.utcnow() - timedelta(hours=delta_tle_hours + 1)
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/tle'):  
        for filename in files:
            print(filename)

            old_tle_date = datetime.strptime(filename, "tle_%d_%m_%Y-%H:%M:%S.txt")
            
            if(old_tle_date > update):
                update = old_tle_date
    
    if(datetime.utcnow() - timedelta(hours=delta_tle_hours) >= update):
        update = datetime.utcnow()
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

def main():
    print(por.tlefile.SATELLITES)
    update_date = update_tle(TLE_URLS)
    satelites.append(Satelite("NOAA 15", place(55, 37, 0.1)))
    print(satelites[0].get_while_loc())
    window = windows.main(satelites[0].get_while_loc, satelites[0].get_orbit_number)

if __name__ == "__main__":
    main()