import shap
import joblib
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

# Setup
os.makedirs('evaluation', exist_ok=True)
print("Script started successfully.")

# 1. Load Resources
try:
    # Check for Tuned Model first, then Standard
    model_path = 'models/best_tuned_model.pkl' if os.path.exists('models/best_tuned_model.pkl') else 'models/best_model.pkl'
    if not os.path.exists(model_path): raise FileNotFoundError("No model found.")

    print(f"Loading Model: {model_path}")
    model = joblib.load(model_path)
    X_train = np.load('data/processed/X_train.npy')
    
    with open('data/processed/feature_names.json', 'r') as f:
        feature_names = json.load(f)

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# 2. Calculate SHAP Values
print("Calculating SHAP values...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)

# Handle different SHAP output formats (List vs 3D Array)
if isinstance(shap_values, list):
    shap_values_survived = shap_values[1]
elif len(np.shape(shap_values)) == 3:
    shap_values_survived = shap_values[:, :, 1]
else:
    shap_values_survived = shap_values

# 3. Generate Summary Plot (Beeswarm)
print("Generating SHAP Summary Plot...")
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values_survived, X_train, feature_names=feature_names, show=False)
plt.title("SHAP Summary: Feature Impact on Survival")
plt.savefig('evaluation/shap_summary.png', bbox_inches='tight')
plt.close()

# 4. Generate SHAP Feature Importance Bar Chart
print("Generating Feature Importance Chart...")

# Calculate Mean |SHAP| (The standard SHAP importance metric)
shap_importance = np.abs(shap_values_survived).mean(axis=0)

# Create DataFrame & Sort
df_imp = pd.DataFrame({'Feature': feature_names, 'Importance': shap_importance})
df_imp = df_imp.sort_values(by='Importance', ascending=False)
df_imp.to_csv('evaluation/feature_importance.csv', index=False)

# Plot
plt.figure(figsize=(10, 8))
sns.barplot(x='Importance', y='Feature', data=df_imp, palette='viridis')
plt.title('Feature Importance (Mean |SHAP Value|)')
plt.xlabel('Average Impact on Model Output')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.savefig('evaluation/feature_importance.png', bbox_inches='tight')
plt.close()

print("\n✅ Analysis complete. All charts saved to 'evaluation/'.")