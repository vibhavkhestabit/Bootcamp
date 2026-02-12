import numpy as np
import json
import os
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

def select_features(train_x_path, train_y_path, output_mask_path):
    # Load ONLY Training Data
    if not os.path.exists(train_x_path):
        raise FileNotFoundError(f"Cannot find {train_x_path}")
        
    X_train = np.load(train_x_path)
    y_train = np.load(train_y_path)
    
    print(f"Selecting features from Training Set: {X_train.shape}")
    
    # RFE with Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    selector = RFE(estimator=model, n_features_to_select=10)
    selector.fit(X_train, y_train)
    
    # Save Mask
    support = selector.support_
    np.save(output_mask_path, support)
    
    print(f"Selection Complete. Saved mask to {output_mask_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    X_TRAIN = os.path.join(BASE_DIR, "data/processed/X_train.npy")
    Y_TRAIN = os.path.join(BASE_DIR, "data/processed/y_train.npy")
    MASK_OUT = os.path.join(BASE_DIR, "data/processed/selected_mask.npy")
    
    select_features(X_TRAIN, Y_TRAIN, MASK_OUT)