import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from sklearn.preprocessing import StandardScaler

# Ensure directory exists
os.makedirs('evaluation', exist_ok=True)

# 1. Load Data & Tuned Model
print("Loading resources...")

try:
    model = joblib.load('models/best_tuned_model.pkl')
    # UPDATED PATH: pointing to data/raw/dataset.csv
    df_train = pd.read_csv('data/raw/dataset.csv')
    print(f"Data loaded: {df_train.shape}")
except FileNotFoundError as e:
    print(f"ERROR: File not found - {e}")
    print("Please check your 'models' folder or 'data/raw' folder.")
    sys.exit(1)

# Preprocessing (Must match training exactly)
features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare']

# Check for missing columns
missing_cols = [col for col in features if col not in df_train.columns]
if missing_cols:
    print(f"ERROR: Missing columns: {missing_cols}")
    sys.exit(1)

X = pd.get_dummies(df_train[features], drop_first=True)
X = X.fillna(X.mean())

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# 2. Create SHAP Explainer
# TreeExplainer is optimized for Random Forest
print("Calculating SHAP values... (This might take a moment)")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_scaled)

# Handle Binary Classification (We want index 1 = 'Survived')
# Random Forest SHAP values are a list [Class 0, Class 1]
if isinstance(shap_values, list):
    shap_values_survived = shap_values[1]
else:
    shap_values_survived = shap_values

# 3. Generate Summary Plot (Global Importance)
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values_survived, X_scaled, show=False)
plt.title("SHAP Summary: Feature Impact on Survival")
plt.savefig('evaluation/shap_summary.png', bbox_inches='tight')
print("Saved: evaluation/shap_summary.png")
plt.close()

# 4. Generate Dependence Plot (Age vs Survival)
plt.figure(figsize=(10, 6))
shap.dependence_plot("Age", shap_values_survived, X_scaled, show=False)
plt.title("SHAP Dependence: Age vs Impact")
plt.savefig('evaluation/shap_dependence_age.png', bbox_inches='tight')
print("Saved: evaluation/shap_dependence_age.png")

print("\nSHAP analysis complete.")