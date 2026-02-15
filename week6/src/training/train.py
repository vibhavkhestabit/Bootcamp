import numpy as np
import pandas as pd
import os
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Sklearn Metrics & Validation
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# The 4 Models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

def load_data(data_dir):
    """Loads the processed arrays from Day 2."""
    X_train = np.load(os.path.join(data_dir, "X_train.npy"))
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_train = np.load(os.path.join(data_dir, "y_train.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))
    return X_train, X_test, y_train, y_test

def train_and_evaluate():
    # Setup Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
    MODEL_DIR = os.path.join(BASE_DIR, "models")
    EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
    
    # Ensure output directories exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(EVAL_DIR, exist_ok=True)

    # 1. Load Data
    X_train, X_test, y_train, y_test = load_data(DATA_DIR)
    print(f"Data loaded. Training size: {X_train.shape[0]} rows.")

# 2. Initialize Models (With Explicit Regularization visible!)
    models = {
        # Logistic Regression
        # penalty='l2': Uses Ridge Regularization (The Equalizer)
        # C=1.0: The strength. Smaller 'C' = Stronger Regularization (Simpler model).
        "Logistic Regression": LogisticRegression(penalty='l2', C=1.0, max_iter=1000, random_state=42),

        # Random Forest
        # Regularization here is "Structural" (limiting tree growth)
        # max_depth=None: No limit (Default). Setting this to 5 or 10 would regularize it.
        # min_samples_leaf=1: Default. Increasing this prevents memorizing single rows.
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_leaf=1, random_state=42),

        # XGBoost
        # reg_lambda=1: L2 Regularization (Standard default).
        # reg_alpha=0: L1 Regularization (Off by default).
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', reg_lambda=1, reg_alpha=0, random_state=42),

        # Neural Network
        # alpha=0.0001: L2 Regularization penalty on the weights.
        "Neural Network": MLPClassifier(alpha=0.0001, max_iter=1000, random_state=42)
    }

    results = {}
    best_model_name = ""
    best_roc_auc = 0
    best_model_instance = None

    # 3. Training Loop
    print("\n--- Starting Model Training & Cross-Validation ---")
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # A. 5-Fold Cross Validation (on Training Set)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"  CV Accuracy (5-fold): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # B. Train on Full Training Set
        model.fit(X_train, y_train)
        
        # C. Predict on Test Set
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] # Get probabilities for ROC-AUC
        
        # D. Calculate Metrics
        metrics = {
            "Accuracy": round(accuracy_score(y_test, y_pred), 4),
            "Precision": round(precision_score(y_test, y_pred), 4),
            "Recall": round(recall_score(y_test, y_pred), 4),
            "F1_Score": round(f1_score(y_test, y_pred), 4),
            "ROC_AUC": round(roc_auc_score(y_test, y_prob), 4)
        }
        
        results[name] = metrics
        print(f"  Test Metrics: {metrics}")
        
        # E. Keep track of the best model (using ROC-AUC as the deciding factor)
        if metrics["ROC_AUC"] > best_roc_auc:
            best_roc_auc = metrics["ROC_AUC"]
            best_model_name = name
            best_model_instance = model

    # 4. Save Metrics to JSON
    metrics_path = os.path.join(EVAL_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ All metrics saved to {metrics_path}")

    # 5. Save the Best Model
    model_path = os.path.join(MODEL_DIR, "best_model.pkl")
    joblib.dump(best_model_instance, model_path)
    print(f"✅ Best Model ({best_model_name}) saved to {model_path}")

    # 6. Plot Confusion Matrix for the Best Model
    y_pred_best = best_model_instance.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Died', 'Survived'], yticklabels=['Died', 'Survived'])
    plt.title(f'Confusion Matrix: {best_model_name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    
    cm_path = os.path.join(EVAL_DIR, "confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"✅ Confusion Matrix plotted and saved to {cm_path}")

if __name__ == "__main__":
    train_and_evaluate()