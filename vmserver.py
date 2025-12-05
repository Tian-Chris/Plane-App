import asyncio
import websockets
import json
import base64
import os
import folium
from ultralytics import YOLO
from angle_finder import coords, querry 

dist_threshold = 100
angle_threshold = 80.0

def detect_plane(base64_data):
    model = YOLO("best.pt")
    img_data = base64.b64decode(base64_data)
    with open("image.jpg", "wb") as f: 
        f.write(img_data)
    results = model.predict("image.jpg", conf=0.6, verbose=False) 
        
    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            if class_name == "AirPlane":                    
                return True                    
    return False

def update_folium_map(lat, lon, plane):
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], icon=folium.Icon()).add_to(m)
    folium.Marker([plane['lat'], plane['lon']], popup=plane['callsign'], icon=folium.Icon(icon="plane")).add_to(m)
    m.save("flight_map.html")

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        lat = data.get("lat")
        lon = data.get("lon")
        alt = data.get("alt")
        heading = data.get("heading") 
        pitch = data.get("pitch")
        base64_image = data.get("image")
        print("Recieved image\n")

        if detect_plane(base64_image):
            print("Plane detected\n")
            location_A = coords(lat, lon, alt)
            plane_targets = querry(location_A) 

            best_match = None
            min_dist_sq = 10000
            
            for plane in plane_targets:
                target_bearing = plane['target_bearing']
                target_elevation = plane['target_elevation']
                plane_dist_sq = plane['dist']

                bearing_diff = abs(heading - target_bearing)
                if bearing_diff > 180:
                    bearing_diff = 360 - bearing_diff
                pitch_diff = abs(pitch - target_elevation)

                if (bearing_diff < angle_threshold and pitch_diff < angle_threshold):
                    if plane_dist_sq < dist_threshold:                            
                        if plane_dist_sq < min_dist_sq:
                            min_dist_sq = plane_dist_sq
                            best_match = plane
                            best_match['bearing_diff'] = bearing_diff
                            best_match['pitch_diff'] = pitch_diff                
            if best_match:
                print(f" Plane is {best_match['callsign']}.")
                print(f" Plane Angle: heading={best_match['target_bearing']}, pitch={best_match['target_elevation']}")
                print(f" Diffs: heading={best_match['bearing_diff']}, pitch ={best_match['pitch_diff']}")
                update_folium_map(lat, lon, best_match)

async def main():
    async with websockets.serve(handler, "0.0.0.0", "8080", max_size=20000000):
        await asyncio.Future()

if __name__ == "__main__":
    if not os.path.exists("flight_map.html"):
        m = folium.Map(location=[0, 0], zoom_start=2)
        m.save("flight_map.html")
        
    print(f"Starting WebSocket server")
    asyncio.run(main())
