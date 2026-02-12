import pandas as pd
import numpy as np
import argparse
import os

def load_data(file_path):
    """Loads the raw dataset."""
    if not os.path.exists(file_path):
        # Tries to find the file relative to the script if running from different dirs
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, file_path)
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully. Shape: {df.shape}")
    return df

def clean_data(df, drop_columns=None, missing_threshold=0.7):
    """
    Universal Cleaning Logic (Corrected Order):
    1. Removes Duplicates (WHILE IDs ARE STILL THERE).
    2. Drops explicit useless columns (IDs, Names, etc).
    3. Drops columns with too many missing values (>70%).
    4. Automagically imputes Missing Values.
    """
    df = df.copy()
    
    # --- STEP 1: Remove Duplicates (Do this FIRST!) ---
    initial_rows = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_rows:
        print(f"Removed {initial_rows - len(df)} duplicate rows.")
    
    # --- STEP 2: Drop explicit useless columns ---
    if drop_columns:
        print(f"Dropping explicit columns: {drop_columns}")
        df = df.drop(columns=[c for c in drop_columns if c in df.columns], errors='ignore')

    # --- STEP 3: Dynamic Column Dropping (Garbage Collection) ---
    missing_percent = df.isnull().mean()
    high_missing_cols = missing_percent[missing_percent > missing_threshold].index.tolist()
    
    if high_missing_cols:
        print(f"Dropping columns with >{int(missing_threshold*100)}% missing: {high_missing_cols}")
        df = df.drop(columns=high_missing_cols)

    # --- STEP 4: Universal Imputation ---
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns

    # A. Handle Numbers (Fill with Median)
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"Filled missing '{col}' with Median: {median_val}")

    # B. Handle Categories (Fill with Mode)
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            if not df[col].mode().empty:
                mode_val = df[col].mode()[0]
                df[col] = df[col].fillna(mode_val)
                print(f"Filled missing '{col}' with Mode: {mode_val}")
            else:
                df[col] = df[col].fillna("Unknown")

    print(f"Cleaning complete. Final Shape: {df.shape}")
    return df

def save_data(df, output_path):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to: {output_path}")

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # We use logic to make sure paths work whether you run from 'src' or 'week6'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Goes up to week6/
    
    RAW_DATA_PATH = os.path.join(BASE_DIR, "data/raw/dataset.csv")
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data/processed/final.csv")
    
    TITANIC_USELESS_COLS = ['PassengerId', 'Name', 'Ticket']

    # --- EXECUTION ---
    print("Starting Data Pipeline...")
    
    # 1. Load
    raw_df = load_data(RAW_DATA_PATH)
    
    # 2. Clean
    clean_df = clean_data(raw_df, drop_columns=TITANIC_USELESS_COLS)
    
    # 3. Save
    save_data(clean_df, PROCESSED_DATA_PATH)
    
    print("Pipeline Completed Successfully.")