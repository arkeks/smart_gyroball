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

# Get the local IP address (works for both Linux and macOS)
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)

if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS="localhost"
fi

# Create a temporary config file to listen on all interfaces
CONFIG_FILE=$(mktemp /tmp/mosquitto_conf.XXXXXX)
cat > "$CONFIG_FILE" <<EOF
listener 1883 $IP_ADDRESS
allow_anonymous true
EOF

# Start Mosquitto broker with the config file
echo "Starting Mosquitto MQTT broker on $IP_ADDRESS..."
mosquitto -c "$CONFIG_FILE" -v

# Clean up config file on exit
trap 'rm -f "$CONFIG_FILE"' EXIT

echo "MQTT broker is running on:"
echo "- MQTT port: $IP_ADDRESS:1883"
echo "- Press Ctrl+C to stop the broker"