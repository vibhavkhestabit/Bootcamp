import pandas as pd
import optuna
import joblib
import json
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

# Ensure directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('tuning', exist_ok=True)

print("Script started successfully.")

# 1. Load Data
print("Loading data...")
try:
    # Load dataset from the raw directory
    df_train = pd.read_csv('data/raw/dataset.csv')
    print(f"Data loaded: {df_train.shape}")
    
    # Check for target column
    if 'Survived' not in df_train.columns:
        print("ERROR: 'Survived' column not found in dataset.csv")
        sys.exit(1)
        
    y = df_train['Survived']
    
except FileNotFoundError:
    print("ERROR: 'data/raw/dataset.csv' not found.")
    print("Please check that you are running this from the 'src' folder.")
    sys.exit(1)

# 2. Preprocessing
print("Preprocessing data...")
features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare']

# Check if required features exist
missing_cols = [col for col in features if col not in df_train.columns]
if missing_cols:
    print(f"ERROR: Missing columns in dataset: {missing_cols}")
    sys.exit(1)

# Encode categorical variables and handle missing values
X = pd.get_dummies(df_train[features], drop_first=True)
X = X.fillna(X.mean())

# Scale features
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# 3. Define the Objective Function for Optuna
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
    
    # 5-Fold Cross-Validation optimizing for ROC-AUC
    score = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc').mean()
    return score

# 4. Run Optimization
print("Starting Optuna optimization (20 trials)...")
optuna.logging.set_verbosity(optuna.logging.WARNING) 
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=20, show_progress_bar=True)

# 5. Results
print("\n--- Best Parameters Found ---")
print(study.best_params)
print(f"Best ROC-AUC: {study.best_value:.4f}")

# 6. Train and Save Best Model
print("Saving best model...")
best_params = study.best_params
best_model = RandomForestClassifier(**best_params, random_state=42)
best_model.fit(X_scaled, y)

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