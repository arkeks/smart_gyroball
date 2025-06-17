import paho.mqtt.client as mqtt


PORT = 1883
TOPIC = "speed/values"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def on_message(client, userdata, message):
    speed = float(message.payload.decode())
    print(f"Received speed: {speed:.2f}")


client = mqtt.Client()

client.on_message = on_message
ip = get_local_ip()
try:
    client.connect(ip, PORT)
    print(f"Connected to MQTT broker at {BROKER}:{PORT}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

client.subscribe(TOPIC)
print(f"Subscribed to topic: {TOPIC}")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nStopping subscriber...")
    client.disconnect()
