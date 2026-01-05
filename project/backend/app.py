from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
import io

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

app = FastAPI(title="Seaweed Identification Backend")

templates = Jinja2Templates(directory="templates")

# =======================
# MODEL CONFIG & LAZY LOAD
# =======================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "final_model.keras"

CLASS_NAMES = ["gracilaria", "kappaphycus"]
IMG_SIZE = (224, 224)
REJECTION_THRESHOLD = 0.70

# Model loading flag
model = None
USE_MOCK_MODEL = True  # Set to False when TensorFlow works

def load_model_once():
    """Load model and dependencies only when first prediction is requested"""
    global model
    
    if model is None:
        if USE_MOCK_MODEL:
            print("⚠️  Using MOCK model (TensorFlow has issues on this system)")
            print("   Set USE_MOCK_MODEL=False in app.py when TensorFlow is fixed")
            model = "mock"
        else:
            print("🔄 Loading TensorFlow and model...")
            try:
                import tensorflow as tf
                import numpy as np
                from PIL import Image
                
                model = {
                    'tf': tf,
                    'np': np,
                    'Image': Image,
                    'keras_model': tf.keras.models.load_model(str(MODEL_PATH))
                }
                print("✅ Model loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                raise

def predict_with_mock(image_bytes):
    """Mock prediction for demonstration when TensorFlow doesn't work"""
    import hashlib
    
    # Simulate processing - use hash to get deterministic but varied results
    hash_val = int(hashlib.md5(image_bytes).hexdigest(), 16)
    
    # Use hash to deterministically pick a class
    idx = hash_val % 2
    
    # Vary confidence more realistically (0.45 to 0.95)
    # This allows some images to be rejected (below 0.70 threshold)
    confidence = 0.45 + (hash_val % 50) / 100  # Between 0.45 and 0.95
    
    if confidence < REJECTION_THRESHOLD:
        return {
            "label": "Non-Seaweed",
            "confidence": confidence,
            "rejected": True
        }
    
    return {
        "label": CLASS_NAMES[idx],
        "confidence": confidence,
        "rejected": False
    }

# =======================
# HOME PAGE
# =======================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =======================
# PREDICT API
# =======================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    print("\n" + "="*60)
    print("📸 New prediction request received")
    print(f"📄 Filename: {file.filename}")

    try:
        # Load model on first request
        load_model_once()
        
        # Read image
        image_bytes = await file.read()
        
        if USE_MOCK_MODEL:
            # Use mock prediction
            result = predict_with_mock(image_bytes)
            print(f"🎭 MOCK Prediction: {result['label'].upper()}")
            print(f"📊 Confidence: {result['confidence']:.2%}")
        else:
            # Real TensorFlow prediction
            from PIL import Image as PILImage
            import numpy as np
            
            img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
            img = img.resize(IMG_SIZE)
            arr = np.array(img, dtype=np.float32)
            arr = np.expand_dims(arr, axis=0)
            arr = model['tf'].keras.applications.efficientnet.preprocess_input(arr)
            
            # Predict
            probs = model['keras_model'].predict(arr, verbose=0)[0]
            idx = int(np.argmax(probs))
            confidence = float(probs[idx])
            
            # Build result
            if confidence < REJECTION_THRESHOLD:
                result = {
                    "label": "Non-Seaweed",
                    "confidence": confidence,
                    "rejected": True
                }
                print(f"🔴 Result: Non-Seaweed")
                print(f"📊 Confidence: {confidence:.2%}")
                print(f"   (Below threshold of {REJECTION_THRESHOLD:.2%})")
            else:
                result = {
                    "label": CLASS_NAMES[idx],
                    "confidence": confidence,
                    "rejected": False
                }
                print(f"✅ Prediction: {CLASS_NAMES[idx].upper()}")
                print(f"📊 Confidence: {confidence:.2%}")
        
        print("="*60 + "\n")
        return result

    except Exception as e:
        print(f"❌ Prediction failed: {repr(e)}")
        print("="*60 + "\n")
        return {"error": str(e)}