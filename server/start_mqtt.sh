#!/bin/bash

# Check if Mosquitto is installed
if ! command -v mosquitto &> /dev/null; then
    echo "Mosquitto is not installed. Please install it first:"
    echo "For macOS: brew install mosquitto"
    echo "For Ubuntu/Debian: sudo apt-get install mosquitto"
    exit 1
fi

# Check if Mosquitto is already running
if pgrep mosquitto > /dev/null; then
    echo "Mosquitto MQTT broker is already running"
    exit 0
fi

# Start Mosquitto broker
echo "Starting Mosquitto MQTT broker..."
mosquitto -v

echo "MQTT broker is running on:"
echo "- MQTT port: localhost:1883" 