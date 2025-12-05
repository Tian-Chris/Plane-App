import numpy as np
import math
import requests

radius_earth = 6378100 #meter
class coords:
    def __init__(self, lat, lon, h):
        self.lat = lat
        self.lon = lon
        self.h = h
        self.convert_to_cartesian()

    #creates a coordinate containing x y z
    # as well as the norm vector to north and vector to east
    def convert_to_cartesian(self):
        self.coord = np.array([(radius_earth + self.h) * np.cos(np.radians(self.lat)) * np.cos(np.radians(self.lon)), 
                               (radius_earth + self.h) * np.cos(np.radians(self.lat)) * np.sin(np.radians(self.lon)),
                               (radius_earth + self.h) * np.sin(np.radians(self.lat))])
        
        self.north = np.array([-np.sin(np.radians(self.lat)) * np.cos(np.radians(self.lon)),
                               -np.sin(np.radians(self.lat)) * np.sin(np.radians(self.lon)),
                               np.cos(np.radians(self.lat))])
        
        self.east  = np.array([-np.sin(np.radians(self.lon)),
                               np.cos(np.radians(self.lon)),
                               0])


def angle_finder(a, b):
    #scaled vector from center of the earth to self
    up = a.coord / np.linalg.norm(a.coord)
    AB_vec = b.coord - a.coord

    #AB projected onto the vertical plane aka up component of AB
    AB_projected = (np.dot(AB_vec, up) / np.dot(up, up)) * up
    AB_horizontal = AB_vec - AB_projected #only horizontal component
    
    cos = np.dot(AB_horizontal, a.north)
    sin = np.dot(AB_horizontal, a.east)
    theta = np.arctan2(sin, cos) * 180 / math.pi

    if theta < 0:
        theta += 360

    phi = np.arcsin(np.dot(AB_vec, up)/np.linalg.norm(AB_vec)) * 180 / math.pi

    return theta, phi

def querry(location):
    url = "https://opensky-network.org/api/states/all"
    
    params = {
        "lamin": location.lat - 0.5,
        "lomin": location.lon - 0.5,
        "lamax": location.lat + 0.5,
        "lomax": location.lon + 0.5
    }
    response = requests.get(url, params=params)
    data = response.json()
    states = data.get("states", [])   
    all_planes = []

    for state in states:
        callsign = state[1].strip()
        lon = state[5]
        lat = state[6]
        alt = state[7] # Barometric altitude in meters

        if lon is not None and lat is not None and alt is not None:
            dist = (location.lon - lon)**2 + (location.lat - lat)**2
            pointB = coords(lat, lon, alt)
            bearing, elevation = angle_finder(location, pointB)

            all_planes.append({
                "callsign": callsign, 
                "lat": lat, 
                "lon": lon, 
                "alt": alt,
                "dist": dist,
                "target_bearing": bearing,
                "target_elevation": elevation,
            })

    return all_planes
