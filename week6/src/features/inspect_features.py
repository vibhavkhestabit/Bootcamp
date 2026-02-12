import numpy as np
import json
import os

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASK_PATH = os.path.join(BASE_DIR, "data/processed/selected_mask.npy")
NAMES_PATH = os.path.join(BASE_DIR, "data/processed/feature_names.json")
OUTPUT_LIST = os.path.join(BASE_DIR, "data/processed/feature_list.json")

# Load
mask = np.load(MASK_PATH)
with open(NAMES_PATH, 'r') as f:
    names = json.load(f)

# Filter
selected_features = [name for name, is_selected in zip(names, mask) if is_selected]

print("\n=== TOP 10 SELECTED FEATURES ===")
for i, feat in enumerate(selected_features, 1):
    print(f"{i}. {feat}")

# Save to JSON (Deliverable)
with open(OUTPUT_LIST, 'w') as f:
    json.dump(selected_features, f, indent=4)
print(f"\nSaved list to {OUTPUT_LIST}")