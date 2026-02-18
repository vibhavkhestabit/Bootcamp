from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import uuid
import os
import csv
from datetime import datetime

# Initialize App
app = FastAPI(title="Titanic Survival Prediction API", version="1.0")

# --- 1. Load Resources (ROBUST PATH FIX) ---

# Get the directory where THIS file (api.py) is currently located
# Example: /app/src/deployment/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to find the 'src' folder
# Example: /app/src/
SRC_DIR = os.path.dirname(CURRENT_DIR)

# Define paths relative to the 'src' directory
MODELS_DIR = os.path.join(SRC_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "best_tuned_model.pkl")
BACKUP_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
LOG_FILE = os.path.join(SRC_DIR, "prediction_logs.csv")

# Load Model & Preprocessor
model = None
preprocessor = None

try:
    # Try loading the tuned model first
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Loaded Tuned Model from: {MODEL_PATH}")
    # Fallback to the baseline model
    elif os.path.exists(BACKUP_PATH):
        model = joblib.load(BACKUP_PATH)
        print(f"⚠️ Tuned model not found. Loaded Backup from: {BACKUP_PATH}")
    else:
        raise FileNotFoundError(f"❌ No model found at {MODEL_PATH} or {BACKUP_PATH}")

    # Load Preprocessor
    if os.path.exists(PREPROCESSOR_PATH):
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print(f"✅ Loaded Preprocessor from: {PREPROCESSOR_PATH}")
    else:
        raise FileNotFoundError(f"❌ Preprocessor not found at {PREPROCESSOR_PATH}")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    print(f"Debug Info - Current Dir: {CURRENT_DIR}")
    print(f"Debug Info - Src Dir: {SRC_DIR}")
    # We raise the error to stop the app if models are missing
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
    """Logs the input and output to a CSV file for monitoring."""
    log_entry = input_data.dict()
    log_entry['request_id'] = request_id
    log_entry['prediction'] = prediction 
    log_entry['probability'] = probability
    log_entry['timestamp'] = datetime.now().isoformat()
    
    # Write header if file doesn't exist
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

def apply_feature_engineering(data: dict):
    df = pd.DataFrame([data])
    
    # 1. Family Features
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
    
    # 2. Wealth/Age Interactions
    df['Fare_Per_Person'] = df['Fare'] / df['FamilySize']
    df['Age_Class'] = df['Age'] * df['Pclass']
    
    # 3. Age Categories
    df['Is_Child'] = (df['Age'] < 10).astype(int)
    df['Is_Senior'] = (df['Age'] > 60).astype(int)
    
    # 4. Title Extraction
    # We use a safe split in case the format is unexpected
    def extract_title(name):
        try:
            return name.split(',')[1].split('.')[0].strip()
        except IndexError:
            return "Mr" # Default fallback
            
    df['Title'] = df['Name'].apply(extract_title)
    common_titles = ['Mr', 'Miss', 'Mrs', 'Master']
    df['Title'] = df['Title'].apply(lambda x: x if x in common_titles else 'Rare')
    
    # 5. Name Length
    df['Name_Length'] = df['Name'].apply(len)
    
    # Drop original Name column as per training logic
    df = df.drop(columns=['Name'])
    
    return df

# --- 4. Endpoints ---
@app.get("/")
def home():
    return {"message": "Titanic API is running. Go to /docs for Swagger UI."}

@app.post("/predict")
def predict(passenger: Passenger):
    request_id = str(uuid.uuid4())
    
    try:
        # A. Convert Input to DataFrame (Feature Engineering)
        raw_df = apply_feature_engineering(passenger.dict())
        
        # B. Transform (Scaling/Encoding)
        processed_data = preprocessor.transform(raw_df)
        
        # C. Predict
        prediction_val = int(model.predict(processed_data)[0])
        probability = float(model.predict_proba(processed_data)[0][1])
        
        # D. Format Output
        prediction_label = "Survived" if prediction_val == 1 else "Dead"
        
        # Extract features for response
        used_features_dict = raw_df.iloc[0].to_dict()

        # E. Log
        log_prediction(request_id, passenger, prediction_val, probability)
        
        return {
            "request_id": request_id,
            "survived_prediction": prediction_label,
            "survival_probability": probability,
            "used_features": used_features_dict,
            "message": "Prediction successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))