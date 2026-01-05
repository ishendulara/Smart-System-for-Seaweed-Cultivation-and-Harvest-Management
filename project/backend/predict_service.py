#!/usr/bin/env python3
"""
Standalone prediction service that loads the model once and listens for requests.
This avoids the TensorFlow segfault issue by keeping the model in memory.
"""
import sys
import json
from pathlib import Path

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
from PIL import Image

# Load model once
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "final_model.keras"

print(f"Loading model from: {MODEL_PATH}", file=sys.stderr)
model = tf.keras.models.load_model(str(MODEL_PATH))
print("Model loaded successfully!", file=sys.stderr)

CLASS_NAMES = ["gracilaria", "kappaphycus"]
IMG_SIZE = (224, 224)
REJECTION_THRESHOLD = 0.70

def predict_image(image_path):
    """Predict seaweed type from image path"""
    try:
        # Load and preprocess image
        img = Image.open(image_path).convert("RGB")
        img = img.resize(IMG_SIZE)
        arr = np.array(img, dtype=np.float32)
        arr = np.expand_dims(arr, axis=0)
        arr = tf.keras.applications.efficientnet.preprocess_input(arr)
        
        # Predict
        probs = model.predict(arr, verbose=0)[0]
        idx = int(np.argmax(probs))
        confidence = float(probs[idx])
        
        if confidence < REJECTION_THRESHOLD:
            return {
                "label": "Non-Seaweed",
                "confidence": confidence,
                "rejected": True
            }
        else:
            return {
                "label": CLASS_NAMES[idx],
                "confidence": confidence,
                "rejected": False
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Read image path from stdin
    for line in sys.stdin:
        image_path = line.strip()
        if not image_path:
            continue
        
        result = predict_image(image_path)
        print(json.dumps(result))
        sys.stdout.flush()
