from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

# -------------------------
# CONFIG
# -------------------------

HARVEST_THRESHOLDS = {
    "kappaphycus": 1500,   # grams
    "gracilaria": 800
}

SPECIES_PARAMS = {
    "kappaphycus": {"K": 1800, "r": 0.12, "t0": 25},
    "gracilaria": {"K": 1000, "r": 0.11, "t0": 26}
}

# -------------------------
# REQUEST MODEL
# -------------------------

class PredictRequest(BaseModel):
    species: str
    initial_weight: float
    start_day: int

# -------------------------
# APP
# -------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# LOGISTIC FUNCTION
# -------------------------

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

def inverse_logistic(weight, K, r, t0):
    # Avoid math errors
    weight = min(max(weight, 1), K - 1)
    return t0 - (1 / r) * np.log((K / weight) - 1)


# -------------------------
# PREDICTION ENDPOINT
# -------------------------

@app.post("/predict")
def predict(data: PredictRequest):

    species = data.species

    if species not in SPECIES_PARAMS:
        return {"error": "Unknown species"}

    K = SPECIES_PARAMS[species]["K"]
    r = SPECIES_PARAMS[species]["r"]
    t0 = SPECIES_PARAMS[species]["t0"]

    initial_weight = data.initial_weight
    start_day = data.start_day

    # Determine biological age of the plant from weight
    biological_day = inverse_logistic(initial_weight, K, r, t0)

    prediction_days = 43
    predictions = []

    for i in range(prediction_days):
        day = start_day + i
        biological_t = biological_day + i

        weight = logistic(biological_t, K, r, t0)

        predictions.append({
            "day": day,
            "weight_g": round(weight, 2)
    })


    # Harvest logic
    threshold = HARVEST_THRESHOLDS[species]
    harvest_day = None

    for p in predictions:
        if p["weight_g"] >= threshold:
            harvest_day = p["day"]
            harvest_weight = p["weight_g"]
            break

    # If not reached within 42 days
    if harvest_day is None:
        harvest_weight = predictions[-1]["weight_g"]

    return {
        "species": species,
        "daily_predictions": predictions,
        "predicted_harvest_day": harvest_day,
        "harvest_weight": round(harvest_weight, 2)
    }

# -------------------------
# IOT (OPTIONAL)
# -------------------------

iot_data = []

@app.post("/iot-data")
def receive_iot(data: dict):
    iot_data.append(data)
    return {"status": "received", "data": data}
