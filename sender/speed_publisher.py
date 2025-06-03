import paho.mqtt.client as mqtt
import time
import random
import math

BROKER = "localhost"
PORT = 1883
TOPIC = "speed/values"

client = mqtt.Client()

try:
    client.connect(BROKER, PORT)
    print(f"Connected to MQTT broker at {BROKER}:{PORT}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

client.loop_start()

current_speed = 0
target_speed = 0
last_update = time.time()

try:
    while True:
        current_time = time.time()
        dt = current_time - last_update
        last_update = current_time

        if random.random() < 0.02:  
            target_speed = random.uniform(0, 100)

        speed_diff = target_speed - current_speed
        current_speed += speed_diff * dt * 2

        noise = random.gauss(0, 0.5)
        current_speed = max(0, current_speed + noise)

        client.publish(TOPIC, f"{current_speed:.2f}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping publisher...")
    client.loop_stop()
    client.disconnect()
