import numpy as np
import optuna
import joblib
import json
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.metrics import roc_auc_score, accuracy_score

# Ensure directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('tuning', exist_ok=True)

print("Script started successfully.")

# 1. Load Processed Data (Train AND Test)
print("Loading processed data...")
try:
    # Define paths explicitly for reliability
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
    MASK_PATH = os.path.join(DATA_DIR, "selected_mask.npy")

    # Load Training Data (For Tuning)
    X_train = np.load(os.path.join(DATA_DIR, 'X_train.npy'))
    y_train = np.load(os.path.join(DATA_DIR, 'y_train.npy')).ravel()
    
    # Load Test Data (For Final Evaluation)
    X_test = np.load(os.path.join(DATA_DIR, 'X_test.npy'))
    y_test = np.load(os.path.join(DATA_DIR, 'y_test.npy')).ravel()
    
    print(f"   Original X_train: {X_train.shape}")

    if os.path.exists(MASK_PATH):
        print(f"Found feature mask at {MASK_PATH}")
        mask = np.load(MASK_PATH)
        
        X_train = X_train[:, mask]
        X_test = X_test[:, mask]
        
        print(f" Applied Mask. New shape: {X_train.shape} (Using {sum(mask)} features)")
    else:
        print(" No selection mask found. Tuning on ALL features.")
    

except FileNotFoundError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# 2. Define the Objective Function (Optimizing on Train Only)
def objective(trial):
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 20),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
        'random_state': 42
    }
    
    model = RandomForestClassifier(**param)
    
    # We optimize for ROC-AUC using Cross-Validation
    score = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc').mean()
    return score

# 3. Run Optimization
print("Starting Optuna optimization (20 trials)...")
optuna.logging.set_verbosity(optuna.logging.WARNING) 
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=20, show_progress_bar=True)

print("\n--- Tuning Complete ---")
print(f"Best CV ROC-AUC: {study.best_value:.4f}")
print("Best Params:", study.best_params)

# 4. Final Evaluation of Tuned Model
print("\n--- Final Evaluation of Tuned Model ---")

# Re-create the best model
best_params = study.best_params
best_model = RandomForestClassifier(**best_params, random_state=42)

# A. Calculate Robust Training Metrics (CV)
cv_results = cross_validate(best_model, X_train, y_train, cv=5, scoring='roc_auc')
train_roc_mean = cv_results['test_score'].mean()
train_roc_std = cv_results['test_score'].std()

# B. Train on Full Training Set
best_model.fit(X_train, y_train)

# C. Calculate Test Metrics (The "Reality Check")
y_prob_test = best_model.predict_proba(X_test)[:, 1]
test_roc = roc_auc_score(y_test, y_prob_test)

# D. Print Comparison
print(f"Training ROC-AUC (CV): {train_roc_mean:.4f} (+/- {train_roc_std:.4f})")
print(f"Test ROC-AUC:          {test_roc:.4f}")

# Check for Overfitting
gap = train_roc_mean - test_roc
if gap > 0.05:
    print(f"  WARNING: Overfitting detected! (Gap: {gap:.4f})")
else:
    print(f"  Model is robust. (Gap: {gap:.4f})")

# 5. Save Results & Model
print("\nSaving results...")

# Ensure Models directory uses absolute path if possible or relative to script
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'models', 'best_tuned_model.pkl')
RESULTS_SAVE_PATH = os.path.join(BASE_DIR, 'tuning', 'results.json')

joblib.dump(best_model, MODEL_SAVE_PATH)

results = {
    "best_params": best_params,
    "training_roc_auc_mean": train_roc_mean,
    "training_roc_auc_std": train_roc_std,
    "test_roc_auc": test_roc,
    "overfitting_gap": gap
}

with open(RESULTS_SAVE_PATH, 'w') as f:
    json.dump(results, f, indent=4)

print(f"Saved: {MODEL_SAVE_PATH}")
print(f"Saved: {RESULTS_SAVE_PATH}")