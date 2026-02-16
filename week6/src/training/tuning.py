import numpy as np
import optuna
import joblib
import json
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# Ensure directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('tuning', exist_ok=True)

print("Script started successfully.")

# 1. Load Processed Data (The Smart Way)
print("Loading processed training data...")
try:
    # Load the arrays we created on Day 2/3
    X_train = np.load('data/processed/X_train.npy')
    y_train = np.load('data/processed/y_train.npy')
    
    # Flatten y_train to ensure it's the right shape (n_samples,) for Sklearn
    y_train = y_train.ravel()
    
    print(f"   X_train loaded: {X_train.shape}")
    print(f"   y_train loaded: {y_train.shape}")

except FileNotFoundError:
    print("ERROR: Processed data not found in 'data/processed/'.")
    print("Please ensure X_train.npy and y_train.npy exist.")
    sys.exit(1)

# 2. Define the Objective Function for Optuna
def objective(trial):
    # Hyperparameter search space
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 20),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
        'random_state': 42
    }
    
    model = RandomForestClassifier(**param)
    
    # 5-Fold Cross-Validation on the processed Training Data
    # We use ROC-AUC as the success metric
    score = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc').mean()
    
    return score

# 3. Run Optimization
print("Starting Optuna optimization (20 trials)...")
optuna.logging.set_verbosity(optuna.logging.WARNING) 
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=20, show_progress_bar=True)

# 4. Results
print("\n--- Best Parameters Found ---")
print(study.best_params)
print(f"Best ROC-AUC: {study.best_value:.4f}")

# 5. Train and Save Best Model
print("Saving best model...")
best_params = study.best_params
best_model = RandomForestClassifier(**best_params, random_state=42)

# Train on the full X_train
best_model.fit(X_train, y_train)

joblib.dump(best_model, 'models/best_tuned_model.pkl')
print("Saved: models/best_tuned_model.pkl")

# Save detailed results to JSON
results = {
    "best_score_roc_auc": study.best_value,
    "best_params": study.best_params
}
with open('tuning/results.json', 'w') as f:
    json.dump(results, f, indent=4)
print("Saved: tuning/results.json")