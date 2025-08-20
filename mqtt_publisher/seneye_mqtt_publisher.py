#!/usr/bin/env python3
"""
Seneye → MQTT publisher.

Publishes a single retained JSON payload to <prefix>/state with keys:
temperature, ph, nh3, par, pur, lux, kelvin, in_water, slide_expired

Matches the schema expected by the Home Assistant Seneye integration (MQTT backend).
"""

import json
import os
import signal
import time
from typing import Optional

import paho.mqtt.client as mqtt

# Lazy import so we can start without device present
from pyseneye.sud import SUDevice, Action

def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

MQTT_HOST = env("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(env("MQTT_PORT", "1883"))
MQTT_USERNAME = env("MQTT_USERNAME", "")
MQTT_PASSWORD = env("MQTT_PASSWORD", "")
MQTT_PREFIX = env("MQTT_PREFIX", "seneye").strip().rstrip("/")
INTERVAL = int(env("INTERVAL", "300"))
HIDRAW_PATH = env("HIDRAW_PATH", "")

STATE_TOPIC = f"{MQTT_PREFIX}/state"
LWT_TOPIC = f"{MQTT_PREFIX}/status"

_running = True
def handle_sigterm(signum, frame):
    global _running
    _running = False

signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)

def make_client() -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"seneye-publisher-{os.getpid()}")
    if MQTT_USERNAME or MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.will_set(LWT_TOPIC, payload="offline", retain=True)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    client.publish(LWT_TOPIC, payload="online", retain=True)
    return client

def read_once() -> Optional[dict]:
    """Read one sample from the Seneye via pyseneye."""
    dev = SUDevice(hidraw_path=HIDRAW_PATH or None)
    try:
        dev.action(Action.ENTER_INTERACTIVE_MODE)
        r = dev.action(Action.SENSOR_READING)
        data = {
            "temperature": getattr(r, "temperature", None),
            "ph": getattr(r, "ph", None),
            "nh3": getattr(r, "nh3", None),
            "par": getattr(r, "par", None),
            "pur": getattr(r, "pur", None),
            "lux": getattr(r, "lux", None),
            "kelvin": getattr(r, "kelvin", None),
            "in_water": bool(getattr(r, "in_water", False)),
            "slide_expired": bool(getattr(r, "slide_expired", False)),
        }
        return data
    finally:
        dev.close()

def main():
    print("Seneye MQTT Publisher starting up...")
    client = make_client()
    print(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
    try:
        while _running:
            try:
                data = read_once()
                if data is not None:
                    payload = json.dumps(data, separators=(",", ":"))
                    client.publish(STATE_TOPIC, payload=payload, retain=True)
                    print("Successfully published sensor data.")
                else:
                    print("Failed to read data, will retry next cycle.")
                    # skip publish; try again next cycle
                    pass
            except Exception as e:
                error_message = f"error: {e}"
                print(f"An error occurred: {error_message}")
                client.publish(LWT_TOPIC, payload=error_message, retain=True)

            # responsive sleep
            for _ in range(INTERVAL):
                if not _running:
                    break
                time.sleep(1)
    finally:
        try:
            print("Shutting down...")
            client.publish(LWT_TOPIC, payload="offline", retain=True)
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
    print("Shutdown complete.")

if __name__ == "__main__":
    main()
