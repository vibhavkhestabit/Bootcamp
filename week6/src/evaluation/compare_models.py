import numpy as np
import joblib
import os
import sys
from sklearn.metrics import roc_auc_score, accuracy_score

print("--- The Ultimate Showdown: Default vs. Tuned ---")

# 1. Load the Test Data (The "Final Exam")
# We must use X_test, not X_train, to compare with Day 3 results
try:
    X_test = np.load('data/processed/X_test.npy')
    y_test = np.load('data/processed/y_test.npy')
    print(f"Test Data Loaded: {X_test.shape}")
except FileNotFoundError:
    print("Error: X_test.npy not found.")
    sys.exit(1)

# 2. Load Both Models
try:
    model_default = joblib.load('models/best_model.pkl') # Day 3
    model_tuned = joblib.load('models/best_tuned_model.pkl') # Day 4
    print("Models Loaded.")
except FileNotFoundError:
    print("Error: Models not found. Make sure you have both .pkl files.")
    sys.exit(1)

# 3. Predict & Score (Day 3 Model)
y_prob_default = model_default.predict_proba(X_test)[:, 1]
roc_default = roc_auc_score(y_test, y_prob_default)

# 4. Predict & Score (Day 4 Model)
y_prob_tuned = model_tuned.predict_proba(X_test)[:, 1]
roc_tuned = roc_auc_score(y_test, y_prob_tuned)

# 5. The Verdict
print("\n--- RESULTS ---")
print(f"Day 3 (Default RF): {roc_default:.4f}")
print(f"Day 4 (Tuned RF):   {roc_tuned:.4f}")

difference = roc_tuned - roc_default
if difference > 0:
    print(f"\n✅ Tuning Improved Performance by {difference*100:.2f}% points!")
elif difference > -0.02:
    print(f"\n⏸ Performance is similar. Tuned model is likely more robust (less overfitting).")
else:
    print(f"\n❌ Tuning hurt performance. The constraints (max_depth=7) might be too strict.")