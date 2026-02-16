import numpy as np
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

def select_features(train_x_path, train_y_path, feature_names_path, output_mask_path, plot_output_path, exclude_features=None):
    if exclude_features is None:
        exclude_features = []

    # 1. Load Data
    if not os.path.exists(train_x_path):
        raise FileNotFoundError(f"Cannot find {train_x_path}")
        
    X_train = np.load(train_x_path)
    y_train = np.load(train_y_path)
    
    with open(feature_names_path, 'r') as f:
        feature_names = json.load(f)
    
    print(f"Original Training Set: {X_train.shape}")
    print(f"Features to Exclude: {exclude_features}")

    # ---------------------------------------------------------
    # 2. FILTERING LOGIC (The New Configuration)
    # ---------------------------------------------------------
    # We need to temporarily drop the excluded features to run RFE
    # But we must remember where they were to rebuild the mask later!
    
    kept_indices = []
    dropped_indices = []
    
    for i, name in enumerate(feature_names):
        if name in exclude_features:
            dropped_indices.append(i)
        else:
            kept_indices.append(i)
            
    # Create the "Clean" X for RFE (without Name_Length)
    X_clean = X_train[:, kept_indices]
    clean_feature_names = [feature_names[i] for i in kept_indices]
    
    print(f"Running RFE on filtered set: {X_clean.shape}")

    # 3. RFE (Recursive Feature Elimination)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    selector = RFE(estimator=model, n_features_to_select=10)
    selector.fit(X_clean, y_train)
    
    clean_support = selector.support_ # Length: 19 (if 1 excluded)
    
    # 4. REBUILD THE FULL MASK (Length: 20)
    # We map the results back to the original slots
    full_mask = np.zeros(len(feature_names), dtype=bool)
    
    # Fill in the calculated choices
    for clean_idx, original_idx in enumerate(kept_indices):
        full_mask[original_idx] = clean_support[clean_idx]
        
    # Ensure excluded ones are strictly False (Redundant but safe)
    for idx in dropped_indices:
        full_mask[idx] = False
        
    # Save the FULL mask so it matches X_train.npy shape
    np.save(output_mask_path, full_mask)
    print(f"Selection Complete. Mask shape restored to: {full_mask.shape}")
    print(f"Saved mask to {output_mask_path}")
    
    # ---------------------------------------------------------
    # 5. VISUALIZATION (Plotting the Clean version)
    # ---------------------------------------------------------
    print("Generating Feature Importance Plot...")
    
    # We fit a model on the CLEAN data for the plot
    model.fit(X_clean, y_train)
    importances = model.feature_importances_
    
    # Create DataFrame (Using only clean names)
    df_importance = pd.DataFrame({
        'Feature': clean_feature_names,
        'Importance': importances,
        'Selected': clean_support
    })
    
    df_importance = df_importance.sort_values(by='Importance', ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=df_importance, 
        x='Importance', 
        y='Feature', 
        hue='Selected', 
        dodge=False, 
        palette={True: 'blue', False: 'lightgray'}
    )
    
    plt.title('Feature Importance (Excluding Name_Length)')
    plt.xlabel('Importance Score')
    plt.ylabel('Feature')
    plt.legend(title='Selected by RFE')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    os.makedirs(os.path.dirname(plot_output_path), exist_ok=True)
    plt.savefig(plot_output_path, bbox_inches='tight')
    print(f"✔ Feature importance plot saved to {plot_output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    X_TRAIN = os.path.join(BASE_DIR, "data/processed/X_train.npy")
    Y_TRAIN = os.path.join(BASE_DIR, "data/processed/y_train.npy")
    FEAT_NAMES = os.path.join(BASE_DIR, "data/processed/feature_names.json")
    
    MASK_OUT = os.path.join(BASE_DIR, "data/processed/selected_mask.npy")
    PLOT_OUT = os.path.join(BASE_DIR, "reports/feature_importance.png")
    
    # --- CONFIGURATION HERE ---
    # Add any feature you want to ban to this list
    select_features(X_TRAIN, Y_TRAIN, FEAT_NAMES, MASK_OUT, PLOT_OUT, exclude_features=["Name_Length"])