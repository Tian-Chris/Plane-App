EE-250 FINAL PROJECT: PLANE DETECTOR
Chris Tian & Timothy Hutapea

Dependencies

This project consists of  a Python server and a 
React Native/Expo Frontend.

The following Python libraries are required:
1. flask 
2. flask-sock 
3. folium (Map visualization)
4. ultralytics 
5. numpy 
6. requests

To install all Python dependencies, run:
pip install flask flask-sock folium ultralytics numpy requests

The following packages are required for the client:
1. expo-camera 
2. expo-location 
3. expo-sensors (Hall effect & IMU data)
*Note that these can only be run on IOS devices, but can be compiled either on macs or through Expo's cloud VMs.

To install all Node dependencies, run:
npm install


The server and client must be on the same local network
1. Open a terminal on the Laptop.
2. Navigate to the server directory containing the Python scripts.
3. Run python3 server.py
(On mac, your ip addr can be determined with: ipconfig getifaddr en0 )


1. Open the React Native project code on your computer.
2. Ensure the IP address matches the Python Server's IP
3. Open a new terminal in the React Native project folder.
4. Start the Expo development server:
   npx expo start
5. Open the Expo Go app on your iPhone and scan the QR code.
6. The app will bundle and launch on the phone,
   In the same terminal, it should log: console:Connected to server


1. Point the camera at the sky
2. Press the start send button to start the image polling
3. On the Laptop, open a web browser and navigate to the local host address
4. Detected planes will appear on the map in the browser and
   image reception & detection will be displayed in terminal
