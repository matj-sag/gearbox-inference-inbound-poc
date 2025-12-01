import os
import time
import ssl
import struct
import random
import base64
import paho.mqtt.client as mqtt
import onnxruntime as ort
import numpy as np

BROKER = "apamamatj.latest.stage.c8y.io"
USER = "t9680/matj"
PASSWORD = os.environ.get("C8Y_PASSWORD")
PORT = 9883
TOPIC = "turbine/gearbox/data"

# Chance per message of failure (tuned for “rare but visible in 10 min”)
FAIL_PROB = 0.05  # ~5 percent

# Load ONNX model once, not 4000 times like a lunatic
session = ort.InferenceSession("gearbox_model.onnx", providers=["CPUExecutionProvider"])
model_input = session.get_inputs()[0].name
model_output = session.get_outputs()[0].name

def classify_with_model(vector):
    """vector: list[float] -> returns model output"""
    arr = np.array([vector], dtype=np.float32)
    result = session.run([model_output], {model_input: arr})
    print(str(result))
    return result[0][0]   # unwrap


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
    return (mode, values, payload)


def main():
    client = mqtt.Client()
    client.username_pw_set(USER, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.connect(BROKER, PORT)
    client.loop_start()

    start = time.time()
    print("Publishing for ~10 minutes...")
    while time.time() - start < 600:
        (mode, values, msg) = generate_message()
        model_pred = classify_with_model(values)
        print(f"[MODEL] Predicted={model_pred[0]:.3f} Actual={mode} Values={values}")
        client.publish(TOPIC, msg)
        time.sleep(1)

    print("Done.")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
