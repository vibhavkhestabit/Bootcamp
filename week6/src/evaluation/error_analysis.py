import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
from sklearn.preprocessing import StandardScaler

# Ensure directory exists
os.makedirs('evaluation', exist_ok=True)

# 1. Load Data & Model
print("Loading resources...")
try:
    model = joblib.load('models/best_tuned_model.pkl')
    # UPDATED PATH: pointing to data/raw/dataset.csv
    df = pd.read_csv('data/raw/dataset.csv')
    print(f"Data loaded: {df.shape}")
except FileNotFoundError as e:
    print(f"ERROR: File not found - {e}")
    sys.exit(1)

y_true = df['Survived']

features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare']
X = pd.get_dummies(df[features], drop_first=True)
X = X.fillna(X.mean())

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# 2. Get Predictions & Probabilities
y_pred = model.predict(X_scaled)
y_prob = model.predict_proba(X_scaled)[:, 1] # Probability of 'Survived'

# 3. Identify Errors
df['Predicted'] = y_pred
df['Probability'] = y_prob
df['Is_Error'] = df['Predicted'] != y_true
df['Error_Magnitude'] = abs(df['Probability'] - df['Survived'])

# Filter for Wrong Predictions
errors = df[df['Is_Error'] == True].copy()

# Sort by "Confidence in Wrong Answer"
# Example: Predicted 0.99 chance of survival, but actually died (Magnitude 0.99)
worst_errors = errors.sort_values('Error_Magnitude', ascending=False).head(10)

print("\n--- Top 10 Worst Model Failures ---")
print(worst_errors[['Name', 'Survived', 'Predicted', 'Probability', 'Error_Magnitude']])

# 4. Save Error CSV
errors.to_csv('evaluation/model_errors.csv', index=False)
print("\nSaved: evaluation/model_errors.csv")

# 5. Visualize Failure Zones
plt.figure(figsize=(10, 6))
sns.scatterplot(data=errors, x='Age', y='Fare', hue='Survived', style='Sex', s=100, palette='viridis')
plt.title("Map of Model Failures (Age vs Fare)")
plt.savefig('evaluation/error_map.png')
print("Saved: evaluation/error_map.png")