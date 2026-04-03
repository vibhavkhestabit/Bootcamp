import pandas as pd
import numpy as np
import joblib
import json
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

# Ensure directory exists
os.makedirs('evaluation', exist_ok=True)

print("Script started successfully.")

# 1. Load Resources
print("Loading resources...")
try:
    model = joblib.load('models/best_tuned_model.pkl')
    X_train = np.load('data/processed/X_train.npy')
    y_train = np.load('data/processed/y_train.npy').ravel()
    
    # Load Raw Data (for Names)
    df_raw = pd.read_csv('data/raw/dataset.csv')
    
    # Load Feature Names (Critical for the Heatmap)
    with open('data/processed/feature_names.json', 'r') as f:
        feature_names = json.load(f)

except Exception as e:
    print(f"ERROR: Missing files - {e}")
    sys.exit(1)

# 2. Get Predictions
print("Identifying failures...")
y_pred = model.predict(X_train)
y_prob = model.predict_proba(X_train)[:, 1]

# ---------------------------------------------------------
# PART A: Instance Analysis (Who failed?)
# ---------------------------------------------------------
# Slice raw data to match X_train length
results = df_raw.iloc[:len(X_train)].copy()

# Add logic to track errors
results['Actual'] = y_train
results['Predicted'] = y_pred
results['Probability'] = y_prob
results['Is_Error'] = results['Predicted'] != results['Actual']
results['Error_Magnitude'] = abs(results['Probability'] - results['Actual'])

# Save the "Worst Failures" CSV
errors = results[results['Is_Error'] == True].copy()
worst_errors = errors.sort_values('Error_Magnitude', ascending=False).head(10)

print("\n--- Top 10 Worst Model Failures ---")
print(worst_errors[['Name', 'Actual', 'Predicted', 'Probability', 'Error_Magnitude']])
errors.to_csv('evaluation/model_errors.csv', index=False)
print("Saved: evaluation/model_errors.csv")

# ---------------------------------------------------------
# PART B: Error Clustering Heatmap (Why did they fail?)
# ---------------------------------------------------------
print("\nGenerating Error Pattern Heatmap...")

# 1. Create a DataFrame of the PROCESSED features
df_features = pd.DataFrame(X_train, columns=feature_names)

# 2. Define the 4 Clusters
conditions = [
    (y_train == 1) & (y_pred == 1), # True Positive
    (y_train == 0) & (y_pred == 0), # True Negative
    (y_train == 0) & (y_pred == 1), # False Positive (Type I)
    (y_train == 1) & (y_pred == 0)  # False Negative (Type II)
]
choices = ['Correct (Survived)', 'Correct (Died)', 'Error (False Pos)', 'Error (False Neg)']

# FIX: Added default='Unknown' to prevent Type Error (String vs Int)
df_features['Result_Type'] = np.select(conditions, choices, default='Unknown')

# 3. Calculate the Mean Feature Values for each Cluster
group_means = df_features.groupby('Result_Type').mean().transpose()

# 4. Normalize (Z-Score)
group_means_norm = (group_means - group_means.mean()) / group_means.std()

# 5. Plot Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(
    group_means_norm, 
    annot=True, 
    fmt=".1f", 
    cmap="RdBu_r", 
    center=0, 
    linewidths=.5
)
plt.title("Error Clustering: Feature Profiles of Failures")
plt.xlabel("Prediction Outcome")
plt.ylabel("Features")

plt.savefig('evaluation/error_analysis_heatmap.png', bbox_inches='tight')
print("✅ Saved: evaluation/error_analysis_heatmap.png")

print("\nAnalysis Complete.")