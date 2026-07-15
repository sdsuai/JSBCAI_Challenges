"""Minimal MQTT pub/sub example for B5 (extra credit).

Needs a broker. Easiest options:
    sudo apt install mosquitto        # Linux (runs on localhost:1883)
    brew install mosquitto            # macOS
Or point BROKER at a public test broker like "test.mosquitto.org"
(fine for this exercise; think about why you'd never ship that).

Install the client library:
    pip install paho-mqtt

Run:  python mqtt_example.py
Then, in another terminal, watch everything with the mosquitto CLI:
    mosquitto_sub -h localhost -t 'robot/#' -v
That second terminal is the fan-out demo: it receives every message with
zero changes to this script. Try opening a third.

This script plays both roles in one process (publishes commands,
subscribes to everything under robot/demo/#) just to show the API. In
your real system the robot and the backend are separate processes with
separate clients.
"""

import json
import threading
import time

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
ROBOT_ID = "demo"

CMD_TOPIC = f"robot/{ROBOT_ID}/cmd"
TELEMETRY_TOPIC = f"robot/{ROBOT_ID}/telemetry"
STATUS_TOPIC = f"robot/{ROBOT_ID}/status"


subscribed = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[mqtt] connected: {reason_code}")
    # '#' is a wildcard: subscribe to everything under robot/demo/
    client.subscribe(f"robot/{ROBOT_ID}/#", qos=1)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    subscribed.set()


def on_message(client, userdata, msg):
    print(f"[mqtt] {msg.topic}: {msg.payload.decode()} "
          f"(qos={msg.qos} retained={msg.retain})")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # Last Will: if this client dies WITHOUT calling disconnect() (kill -9,
    # network cut), the BROKER publishes this on our behalf. retain=True
    # means new subscribers immediately get the last status without waiting.
    client.will_set(STATUS_TOPIC, payload="offline", qos=1, retain=True)

    client.connect(BROKER, PORT, keepalive=30)
    client.loop_start()  # network loop runs in a background thread

    # Wait until our own subscription is confirmed, or messages we publish
    # in the next few lines can beat the SUBACK and never echo back to us.
    # connect() returning does NOT mean you're subscribed — everything in
    # MQTT is asynchronous.
    if not subscribed.wait(timeout=5):
        raise TimeoutError("broker never confirmed subscription")

    # Announce we're alive (retained, so late joiners see it too)
    client.publish(STATUS_TOPIC, "online", qos=1, retain=True)

    # Commands get QoS 1 (broker guarantees delivery at least once).
    # Telemetry gets QoS 0 (fire and forget — same reasoning as UDP).
    for i in range(5):
        cmd = {"id": i, "action": "move_to", "params": {"x": i * 0.1, "y": 1.0}}
        client.publish(CMD_TOPIC, json.dumps(cmd), qos=1)
        telemetry = {"seq": i, "x": i * 0.1, "y": 1.0, "battery": 90 - i}
        client.publish(TELEMETRY_TOPIC, json.dumps(telemetry), qos=0)
        time.sleep(1)

    # Graceful shutdown: say goodbye ourselves (the Will only fires on
    # UNgraceful death — test that with kill -9 while this sleeps).
    client.publish(STATUS_TOPIC, "offline", qos=1, retain=True)
    time.sleep(0.5)
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
