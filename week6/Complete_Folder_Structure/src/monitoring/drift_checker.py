import pandas as pd
import numpy as np
import os
import json
import sys
from datetime import datetime

LOG_FILE = "prediction_logs.csv"
BASELINE_FILE = "models/training_baselines.json"
REPORT_FILE = "monitoring/drift_report.json"

def load_baselines():
    if not os.path.exists(BASELINE_FILE):
        print("Error: Baseline file not found. Run src/features/build_features.py first.")
        sys.exit(1)
    with open(BASELINE_FILE, 'r') as f:
        return json.load(f)

def check_drift():
    # 1. Load Baselines
    baselines = load_baselines()
    BASELINE_AGE = baselines['age_mean']
    BASELINE_FARE = baselines['fare_mean']
    BASELINE_SURVIVAL = baselines['survival_rate']

    report = {
        "timestamp": datetime.now().isoformat(),
        "drift_detected": False,
        "metrics": {}
    }

    # 2. Load Logs
    if not os.path.exists(LOG_FILE):
        print("No logs found.")
        return
        
    logs_df = pd.read_csv(LOG_FILE)
    if len(logs_df) < 5:
        print(f"Not enough data ({len(logs_df)} samples). Need at least 5.")
        return

    print(f"--- Drift Report ({len(logs_df)} samples) ---")

    # --- Check Age ---
    curr_age = logs_df['Age'].mean()
    age_diff = abs(curr_age - BASELINE_AGE)
    # Rounding to .4f for the JSON report
    report['metrics']['age'] = {
        "current": round(float(curr_age), 4), 
        "baseline": round(float(BASELINE_AGE), 4), 
        "diff": round(float(age_diff), 4)
    }
    
    if age_diff > 5.0:
        print(f"AGE DRIFT: Shifted by {age_diff:.4f}")
        report['drift_detected'] = True
    else:
        print(f"Age is stable: {curr_age:.4f}")

    # --- Check Fare ---
    curr_fare = logs_df['Fare'].mean()
    fare_diff = abs(curr_fare - BASELINE_FARE)
    # Rounding to .4f for the JSON report
    report['metrics']['fare'] = {
        "current": round(float(curr_fare), 4), 
        "baseline": round(float(BASELINE_FARE), 4), 
        "diff": round(float(fare_diff), 4)
    }

    if fare_diff > 10.0:
        print(f"FARE DRIFT: Shifted by {fare_diff:.4f}")
        report['drift_detected'] = True
    else:
        print(f"Fare is stable: {curr_fare:.4f}")

    # --- Check Survival ---
    curr_surv = pd.to_numeric(logs_df['prediction'], errors='coerce').mean()
    surv_diff = abs(curr_surv - BASELINE_SURVIVAL)
    # Rounding to .4f for the JSON report
    report['metrics']['survival'] = {
        "current": round(float(curr_surv), 4), 
        "baseline": round(float(BASELINE_SURVIVAL), 4), 
        "diff": round(float(surv_diff), 4)
    }

    print(f"Current Survival Rate: {curr_surv:.4f}")
    if surv_diff > 0.15:
        print("ALERT: Model is predicting significantly differently than training baseline.")
        report['drift_detected'] = True
    else:
        print("Output distribution looks stable.")

    # Save Report
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    check_drift()