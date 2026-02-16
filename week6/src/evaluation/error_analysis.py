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
    # Load the Tuned Model
    model = joblib.load('models/best_tuned_model.pkl')
    
    # Load the EXACT data the model was trained on
    X_train = np.load('data/processed/X_train.npy')
    y_train = np.load('data/processed/y_train.npy').ravel()
    
    # Load Raw Data just for the Names (to identify the people)
    df_raw = pd.read_csv('data/raw/dataset.csv')
    
    # Load Feature Names for the plot labels
    with open('data/processed/feature_names.json', 'r') as f:
        feature_names = json.load(f)

except Exception as e:
    print(f"ERROR: Missing files - {e}")
    sys.exit(1)

# 2. Get Predictions
print("Identifying failures using X_train...")
y_pred = model.predict(X_train)
y_prob = model.predict_proba(X_train)[:, 1]

# 3. Identify Errors
# We slice df_raw to match the length of X_train (just in case they differ)
results = df_raw.iloc[:len(X_train)].copy()
results['Predicted'] = y_pred
results['Probability'] = y_prob
results['Actual'] = y_train
results['Is_Error'] = results['Predicted'] != results['Actual']
results['Error_Magnitude'] = abs(results['Probability'] - results['Actual'])

errors = results[results['Is_Error'] == True].copy()
worst_errors = errors.sort_values('Error_Magnitude', ascending=False).head(10)

print("\n--- Top 10 Worst Model Failures ---")
print(worst_errors[['Name', 'Actual', 'Predicted', 'Probability', 'Error_Magnitude']])

# 4. Save Outputs
errors.to_csv('evaluation/model_errors.csv', index=False)
print("\nSaved: evaluation/model_errors.csv")

# 5. Visualize (Using the indices from the processed features)
if "Age" in feature_names and "Fare" in feature_names:
    age_idx = feature_names.index("Age")
    fare_idx = feature_names.index("Fare")
    
    plt.figure(figsize=(10, 6))
    # We use the raw values for plotting so they are easier to read
    sns.scatterplot(data=errors, x='Age', y='Fare', hue='Actual', style='Sex', s=100, palette='viridis')
    plt.title("Map of Model Failures (Age vs Fare)")
    plt.savefig('evaluation/error_map.png')
    print("Saved: evaluation/error_map.png")