import shap
import joblib
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Ensure directory exists
os.makedirs('evaluation', exist_ok=True)

print("Script started successfully.")

# 1. Load Resources
print("Loading model and processed data...")
try:
    # PRIORITY: Try loading the Tuned Model (Day 4)
    if os.path.exists('models/best_tuned_model.pkl'):
        model_path = 'models/best_tuned_model.pkl'
        print(f"   -> Loading Tuned Model: {model_path}")
    # FALLBACK: Day 3 Model
    elif os.path.exists('models/best_model.pkl'):
        model_path = 'models/best_model.pkl'
        print(f"   -> Loading Standard Model: {model_path}")
    else:
        raise FileNotFoundError("No model found in 'models/' directory.")

    model = joblib.load(model_path)
    
    # Load Processed Data (Fast & Consistent)
    X_train = np.load('data/processed/X_train.npy')
    
    # Load Feature Names (For readable plots)
    with open('data/processed/feature_names.json', 'r') as f:
        feature_names = json.load(f)
        
    print(f"   Training data loaded: {X_train.shape}")
    print(f"   Features: {feature_names}")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# 2. Create SHAP Explainer
print("Calculating SHAP values... (This might take a moment)")

# TreeExplainer is optimized for Random Forests
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)

# Handle Binary Classification (Select Class 1 = Survived)
if isinstance(shap_values, list):
    shap_values_survived = shap_values[1]
else:
    shap_values_survived = shap_values

# 3. Generate Summary Plot
print("Generating Summary Plot...")
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values_survived, X_train, feature_names=feature_names, show=False)
plt.title("SHAP Summary: Feature Impact on Survival")
plt.savefig('evaluation/shap_summary.png', bbox_inches='tight')
print("   Saved: evaluation/shap_summary.png")
plt.close()

# 4. Generate Dependence Plot (Age)
if "Age" in feature_names:
    print("Generating Dependence Plot for 'Age'...")
    age_idx = feature_names.index("Age")
    
    plt.figure(figsize=(10, 6))
    shap.dependence_plot(age_idx, shap_values_survived, X_train, feature_names=feature_names, show=False)
    plt.title("SHAP Dependence: Age vs Impact")
    plt.savefig('evaluation/shap_dependence_age.png', bbox_inches='tight')
    print("   Saved: evaluation/shap_dependence_age.png")
else:
    print("Skipping Age plot: 'Age' feature not found.")

print("\nSHAP analysis complete.")