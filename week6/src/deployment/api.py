from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import uuid
import os
import csv
from datetime import datetime

try:
    from src.features.transformers import TitanicFeatureEngineer
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.features.transformers import TitanicFeatureEngineer

# Initialize App
app = FastAPI(title="Titanic Survival Prediction API", version="1.0")

# --- 1. Load Resources ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
MODELS_DIR = os.path.join(SRC_DIR, "models")
PROCESSED_DIR = os.path.join(SRC_DIR, "data", "processed")

MODEL_PATH = os.path.join(MODELS_DIR, "best_tuned_model.pkl")
BACKUP_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
MASK_PATH = os.path.join(PROCESSED_DIR, "selected_mask.npy")
LOG_FILE = os.path.join(SRC_DIR, "prediction_logs.csv")

# Global Variables
model = None
preprocessor = None
selection_mask = None
feature_engineer = TitanicFeatureEngineer() 

try:
    # A. Load Model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f" Loaded Tuned Model: {MODEL_PATH}")
    elif os.path.exists(BACKUP_PATH):
        model = joblib.load(BACKUP_PATH)
        print(f" Loaded Backup Model: {BACKUP_PATH}")
    else:
        raise FileNotFoundError(f" No model found at {MODEL_PATH}")

    # B. Load Preprocessor
    if os.path.exists(PREPROCESSOR_PATH):
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print(f" Loaded Preprocessor: {PREPROCESSOR_PATH}")
    else:
        raise FileNotFoundError(f" No preprocessor found at {PREPROCESSOR_PATH}")

    # C. Load Selection Mask
    if os.path.exists(MASK_PATH):
        selection_mask = np.load(MASK_PATH)
        print(f" Loaded Feature Selection Mask: Keeping {sum(selection_mask)} features")
    else:
        print(" No selection mask found. API might crash if model expects fewer features.")

except Exception as e:
    print(f" CRITICAL ERROR: {e}")
    raise e

# --- 2. Input Schema ---
class Passenger(BaseModel):
    Pclass: int
    Name: str
    Sex: str
    Age: float
    SibSp: int
    Parch: int
    Fare: float
    Embarked: str

# --- 3. Helper Functions ---
def log_prediction(request_id, input_data, prediction, probability):
    """Logs the input and output to a CSV file."""
    log_entry = input_data.dict()
    log_entry['request_id'] = request_id
    log_entry['prediction'] = prediction 
    log_entry['probability'] = probability
    log_entry['timestamp'] = datetime.now().isoformat()
    
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

# --- 4. Endpoints ---
@app.get("/")
def home():
    return {"message": "Titanic API Running"}

@app.post("/predict")
def predict(passenger: Passenger):
    request_id = str(uuid.uuid4())
    
    try:
        input_df = pd.DataFrame([passenger.dict()])
        engineered_df = feature_engineer.transform(input_df)
        processed_data = preprocessor.transform(engineered_df)
        if selection_mask is not None:
            processed_data = processed_data[:, selection_mask]
            
        prediction_val = int(model.predict(processed_data)[0])
        probability = float(model.predict_proba(processed_data)[0][1])
        prediction_label = "Survived" if prediction_val == 1 else "Dead"

        log_prediction(request_id, passenger, prediction_val, probability)
        
        return {
            "request_id": request_id,
            "prediction": prediction_label,
            "probability": probability,
            "message": "Success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))