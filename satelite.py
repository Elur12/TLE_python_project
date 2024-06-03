import pyorbital as por
from pyorbital.orbital import Orbital
from datetime import datetime, UTC, timedelta
import requests
import os
from dataclasses import dataclass

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

satelites = {}

update_date = datetime.now(UTC) - timedelta(hours=delta_tle_hours + 1)

@dataclass
class place:
    lat: float = 0
    lon: float = 0
    alt: float = 0 #On km

def TLE(func):
    def wrapper():
        if(datetime.now(UTC) - timedelta(hours=delta_tle_hours) >= update_date):
            update_date = update_tle(TLE_URLS)
        func()
    return wrapper

class Sattelite():
    my_place: place
    orb: Orbital
    def __init__(self, name: str, place: place) -> None:
        self.my_place = place
        self.orb = Orbital(name, line1=satelites[name][0], line2=satelites[name][1])
    #@TLE
    def get_location(self):
        return self.orb.get_lonlatalt(datetime.now(UTC))
    def get_observer(self):
        return self.orb.get_observer_look(datetime.now(UTC), self.my_place.lon, self.my_place.lat, self.my_place.alt)





def update_tle(urls) -> str:
    update = datetime.now(UTC) - timedelta(hours=delta_tle_hours + 1)
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/tle'):  
        for filename in files:
            print(filename)

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
            satelites.update({name : (line1, line2)})
    return update

if __name__ == "__main__":
    print(por.tlefile.SATELLITES)
    update_tle(TLE_URLS)
    g = Sattelite("NOAA 15", place(55, 37, 0.1))
    #windows.main()
    while True:
        print(g.get_location())