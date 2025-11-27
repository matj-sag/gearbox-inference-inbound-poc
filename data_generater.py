import time
import ssl
import struct
import random
import base64
import paho.mqtt.client as mqtt

BROKER = "your-broker.example.com"
PORT = 8883
TOPIC = "turbine/gearbox/data"

# Chance per message of failure (tuned for “rare but visible in 10 min”)
FAIL_PROB = 0.02  # ~2 percent

def generate_fft_pattern(mode):
    # Base patterns for each class
    base = {
        0: [0.2, 0.25, 0.3, 0.4, 0.45, 0.3, 0.25, 0.2],        # normal
        1: [0.2, 0.3, 0.6, 1.1, 0.9, 0.5, 0.3, 0.25],          # early bearing
        2: [0.25, 0.35, 1.3, 0.7, 1.5, 0.6, 0.35, 0.25],       # tooth damage
        3: [0.3, 0.35, 0.4, 0.7, 1.4, 0.8, 0.45, 0.3],         # misalignment
    }[mode]
    # Add small noise
    return [x + random.uniform(-0.05, 0.05) for x in base]

def generate_message():
    # Pick mode
    mode = 0
    if random.random() < FAIL_PROB:
        mode = random.choice([1, 2, 3])

    fft = generate_fft_pattern(mode)

    # Temperature and torque drift toward failure states
    if mode == 0:
        temp = 55 + random.uniform(-2, 2)
        torque = 320 + random.uniform(-10, 10)
    elif mode == 1:
        temp = 60 + random.uniform(-2, 3)
        torque = 330 + random.uniform(-15, 15)
    elif mode == 2:
        temp = 62 + random.uniform(0, 3)
        torque = 310 + random.uniform(-20, 20)
    elif mode == 3:
        temp = 58 + random.uniform(-2, 2)
        torque = 300 + random.uniform(-25, 25)

    values = fft + [temp, torque]

    # Pack 10 floats into binary
    payload = struct.pack(">10f", *values)

    # Base64 encode for Analytics Builder
    return base64.b64encode(payload).decode("ascii")


def main():
    client = mqtt.Client()
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(BROKER, PORT)
    client.loop_start()

    start = time.time()
    print("Publishing for ~10 minutes...")
    while time.time() - start < 600:
        msg = generate_message()
        client.publish(TOPIC, msg)
        time.sleep(1)

    print("Done.")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
