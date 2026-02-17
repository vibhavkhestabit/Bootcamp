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

# --- 1. Load Resources ---
MODEL_PATH = "models/best_tuned_model.pkl"
# Fallback if tuned model doesn't exist
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "models/best_model.pkl"

PREPROCESSOR_PATH = "models/preprocessor.pkl"
LOG_FILE = "prediction_logs.csv"

# Load Model & Preprocessor
try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print("✅ Model and Preprocessor loaded successfully.")
except Exception as e:
    print(f"❌ Error loading files: {e}")
    # We don't exit here so the app can start and show errors if hit

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
    # We log the INTEGER (0/1) so drift_checker can calculate means later
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
    """Replicates the logic from build_features.py"""
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
    df['Title'] = df['Name'].apply(lambda x: x.split(',')[1].split('.')[0].strip())
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
        # The preprocessor expects specific columns. The order matches the training DataFrame.
        processed_data = preprocessor.transform(raw_df)
        
        # C. Predict
        # Get the raw integer (0 or 1) for logic
        prediction_val = int(model.predict(processed_data)[0])
        probability = float(model.predict_proba(processed_data)[0][1])
        
        # D. Format Output
        # Convert integer to readable string
        prediction_label = "Survived" if prediction_val == 1 else "Dead"
        
        # Extract the engineered features to show back to the user
        # (Converts the single-row DataFrame to a dictionary)
        used_features_dict = raw_df.iloc[0].to_dict()

        # E. Log
        # We log the original INTEGER 'prediction_val' to keep math easy for drift detection
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