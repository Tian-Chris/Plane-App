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
    #assuming you aren't at the north poll cause then 1 degree lon is like 0 km
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": location.lat - 0.5,
        "lomin": location.lon - 0.5,
        "lamax": location.lat + 0.5,
        "lomax": location.lon + 0.5
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        index = 0
        dist = 0
        for i in range(len(data["states"])):
            callsign = data["states"][i][1].strip()
            lon = data["states"][i][5]
            lat = data["states"][i][6]
            alt = data["states"][i][7]
            print(f"{i}: {callsign} at lat {lat}, lon {lon}, altitude {alt} m")
            # it was messing up cause it was choosing planes with no alt
            if alt is not None and np.sqrt((location.lon - lon)**2 + (location.lat - lat)**2) < dist or dist == 0:
                dist = np.sqrt((location.lon - lon)**2 + (location.lat - lat)**2)
                index = i
        callsign = data["states"][i][1].strip()
        lat = data["states"][index][6]
        lon = data["states"][index][5]
        baromic_altitude = data["states"][index][7]
        print(f"\nchosen plane: {callsign} at lat {lat}, lon {lon}, altitude {baromic_altitude} m\n")
        pointB = coords(lat, lon, baromic_altitude)
        return angle_finder(location, pointB)
    
    else:
        print(f"Error: {response.status_code}")
        return 0, 0


if __name__ == "__main__":
    lat1, lon1, h1 = 34.0522, -118.2437, 0
    
    pointA = coords(lat1, lon1, h1)
    theta, phi = querry(pointA)
    print(f"theta = {theta:.2f}°")
    print(f"phi = {phi:.2f}° \n")