import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "speed/values"



def on_message(client, userdata, message):
    speed = float(message.payload.decode())
    print(f"Received speed: {speed:.2f}")


client = mqtt.Client()

client.on_message = on_message

try:
    client.connect(BROKER, PORT)
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
