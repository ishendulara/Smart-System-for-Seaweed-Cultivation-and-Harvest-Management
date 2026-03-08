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
print(f"📂 Model path set to: {MODEL_PATH}")
CLASS_NAMES = ["gracilaria", "kappaphycus", "non_seaweed"]
IMG_SIZE = (224, 224)

# Confidence thresholds for each class
CLASS_THRESHOLDS = {
    "gracilaria": 0.70,    # Higher threshold for seaweed species
    "kappaphycus": 0.70,   # Higher threshold for seaweed species  
    "non_seaweed": 0.50    # Lower threshold for non-seaweed (minority class)
}
REJECTION_THRESHOLD = 0.70  # Default threshold if not using class-specific

# Model loading flag
model = None
USE_MOCK_MODEL = False  # Using real trained model

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
    
    # Use hash to deterministically pick a class (now 3 classes)
    idx = hash_val % 3
    
    # Vary confidence more realistically (0.40 to 0.95)
    confidence = 0.40 + (hash_val % 55) / 100  # Between 0.40 and 0.95
    
    predicted_class = CLASS_NAMES[idx]
    class_threshold = CLASS_THRESHOLDS.get(predicted_class, REJECTION_THRESHOLD)
    
    if confidence < class_threshold:
        return {
            "label": "Unknown",
            "confidence": confidence,
            "rejected": True,
            "reason": f"Confidence {confidence:.2%} below threshold {class_threshold:.2%}"
        }
    
    return {
        "label": predicted_class,
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
            predicted_class = CLASS_NAMES[idx]
            
            # Get class-specific threshold
            class_threshold = CLASS_THRESHOLDS.get(predicted_class, REJECTION_THRESHOLD)
            
            # Build result with class-specific threshold
            if confidence < class_threshold:
                result = {
                    "label": "Unknown",
                    "confidence": confidence,
                    "rejected": True,
                    "predicted_class": predicted_class,
                    "reason": f"Low confidence ({confidence:.2%}) for {predicted_class}"
                }
                print(f"🔴 Result: Unknown (Low Confidence)")
                print(f"📊 Predicted: {predicted_class.upper()} with {confidence:.2%}")
                print(f"   (Below {predicted_class} threshold of {class_threshold:.2%})")
            else:
                result = {
                    "label": predicted_class,
                    "confidence": confidence,
                    "rejected": False
                }
                # Different emoji for non_seaweed vs seaweed species
                emoji = "🌊" if predicted_class in ["gracilaria", "kappaphycus"] else "🚫"
                print(f"{emoji} Prediction: {predicted_class.upper()}")
                print(f"📊 Confidence: {confidence:.2%}")
                
                # Show all class probabilities for debugging
                print(f"📈 All probabilities:")
                for i, prob in enumerate(probs):
                    print(f"   {CLASS_NAMES[i]}: {prob:.2%}")
        
        print("="*60 + "\n")
        return result

    except Exception as e:
        print(f"❌ Prediction failed: {repr(e)}")
        print("="*60 + "\n")
        return {"error": str(e)}