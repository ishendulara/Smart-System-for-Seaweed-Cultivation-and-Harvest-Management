import time
import requests
import random

API_URL = "http://127.0.0.1:8000/iot-data"

weight = 30

for day in range(1, 43):
    growth = random.uniform(5, 12)
    weight += growth

    payload = {
        "day": day,
        "weight": round(weight, 2)
    }

    requests.post(API_URL, json=payload)
    print("Sent:", payload)

    time.sleep(1)
