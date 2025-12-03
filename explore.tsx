import { CameraView, useCameraPermissions } from "expo-camera";
import * as Location from "expo-location";
import { DeviceMotion } from "expo-sensors";
import { useEffect, useRef, useState } from "react";
import { Button, Text, View } from "react-native";

type Telemetry = {
  lat: number;
  lon: number;
  alt: number;
  heading: number;
  pitch: number;
};

export default function App() {
  const [permission, requestPermission] = useCameraPermissions();
  const [heading, setHeading] = useState<Location.LocationHeadingObject | null>(null);
  const [motion, setMotion] = useState<any>(null);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [serverMsg, setServerMsg] = useState("");
  const [autoSend, setAutoSend] = useState(false);
  const cameraRef = useRef<any>(null);
  const ws = useRef<WebSocket | null>(null);

  DeviceMotion.setUpdateInterval(100);

  //connects to server
  useEffect(() => {
    setup();
  }, []);

  useEffect(() => {
    if (!autoSend) return;
    const interval = setInterval(() => {
      sendImageToServer();
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [autoSend]);

  async function setup() {
    const sub1 = DeviceMotion.addListener((d) => setMotion(d));
    const sub2 = await Location.watchHeadingAsync((d) => setHeading(d));
    const response = await Location.requestForegroundPermissionsAsync();
    if (response.status !== "granted") return;

    const loc = await Location.getCurrentPositionAsync({});
    setLocation(loc);
    ws.current = new WebSocket("ws://172.20.10.2:8080");
    ws.current.onmessage = (event) => setServerMsg(event.data);

    return () => {
      sub1.remove();
      sub2.remove();
      ws.current?.close();
    };
  }
  
  async function sendImageToServer() {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;

    const telem: Telemetry = {
      lat: location.coords.latitude,
      lon: location.coords.longitude,
      alt: location.coords.altitude ?? 0,
      heading: heading.trueHeading ?? 0,
      pitch: (motion.rotation.beta * 180) / Math.PI,
    };

    const photo = await cameraRef.current.takePictureAsync({
      base64: true,
      quality: 0.6,
    });

    const payload = {
      type: "telemetry_scan",
      image: photo.base64,
      telemetry: telem,
    };

    ws.current.send(JSON.stringify(payload));
  }

  //ui
  if (!permission?.granted) {
    return (
      <View>
        <Text>camera permission</Text>
        <Text onPress={requestPermission}>Enable Camera</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <CameraView ref={cameraRef} style={{ flex: 1 }}/>
        {location && (
          <Text style={{ color: "white"}}>
            Heading: {heading?.trueHeading?.toFixed(1)}{"\n"}
            Pitch: {motion?.rotation?.beta?.toFixed(1)}{"\n"}
            Lat: {location.coords.latitude.toFixed(1)}, Lon: {location.coords.longitude.toFixed(1)}{"\n"}
            Server: {serverMsg}
          </Text>
        )}
        <Button
          title={autoSend ? "STOP SEND" : "START SEND"}
          onPress={() => setAutoSend(!autoSend)}
        />
      </View>
  );
}


