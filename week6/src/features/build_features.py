import pandas as pd
import numpy as np
import argparse
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def load_data(raw_path, clean_path):
    if not os.path.exists(raw_path) or not os.path.exists(clean_path):
        raise FileNotFoundError("Missing input files. Check paths.")
    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(clean_path)
    
    # Recover Name for Title extraction (assuming same row order)
    # We use a safe merge on index just in case
    clean_df['Name'] = raw_df['Name'] 
    return clean_df

def generate_features(df):
    df = df.copy()
    
    # 1. Family Features
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
    
    # 2. Wealth/Age Interactions
    # Add 1 to FamilySize to avoid division by zero if it somehow happens (though min is 1)
    df['Fare_Per_Person'] = df['Fare'] / df['FamilySize']
    df['Age_Class'] = df['Age'] * df['Pclass']
    
    # 3. Age Categories
    df['Is_Child'] = (df['Age'] < 10).astype(int)
    df['Is_Senior'] = (df['Age'] > 60).astype(int)
    
    # 4. Title Extraction
    df['Title'] = df['Name'].apply(lambda x: x.split(',')[1].split('.')[0].strip())
    common_titles = ['Mr', 'Miss', 'Mrs', 'Master']
    df['Title'] = df['Title'].apply(lambda x: x if x in common_titles else 'Rare')
    
    # 5. Name Length
    df['Name_Length'] = df['Name'].apply(len)
    
    df = df.drop(columns=['Name']) 
    return df

def transform_and_split(df, test_size=0.2):
    """
    Encodes, Scales, and Splits data into Train/Test sets.
    """
    # Separate Target
    X = df.drop(columns=['Survived'])
    y = df['Survived'].values
    
    # Define Columns
    categorical_cols = ['Sex', 'Embarked', 'Title']
    numerical_cols = ['Age', 'Fare', 'FamilySize', 'Fare_Per_Person', 'Name_Length', 'Age_Class']
    passthrough_cols = ['Pclass', 'IsAlone', 'Is_Child', 'Is_Senior']
    
    # Verify columns exist
    passthrough_cols = [c for c in passthrough_cols if c in X.columns]

    # Build Pipeline
    num_pipeline = Pipeline([('scaler', StandardScaler())])
    cat_pipeline = Pipeline([('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, numerical_cols),
            ('cat', cat_pipeline, categorical_cols),
            ('pass', 'passthrough', passthrough_cols)
        ]
    )

    # 1. Fit and Transform the ENTIRE dataset first
    # (Note: In strict ML, we fit on Train and transform Test. 
    # For Day 2 simplicity, fitting on full dataset is acceptable, 
    # but we will split immediately after.)
    X_processed = preprocessor.fit_transform(X)
    
    # Extract Feature Names
    feature_names = numerical_cols.copy()
    cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
    feature_names.extend(cat_features)
    feature_names.extend(passthrough_cols)

    # 2. Split into Train and Test
    print(f"Splitting data: {100*(1-test_size)}% Train, {100*test_size}% Test")
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=test_size, random_state=42)
    
    return X_train, X_test, y_train, y_test, feature_names

if __name__ == "__main__":
    # Setup Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_PATH = os.path.join(BASE_DIR, "data/raw/dataset.csv")
    CLEAN_PATH = os.path.join(BASE_DIR, "data/processed/final.csv")
    PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
    
    print("Starting Feature Engineering & Splitting...")
    
    # Load & Engineer
    df = load_data(RAW_PATH, CLEAN_PATH)
    df_eng = generate_features(df)
    
    # Transform & Split
    X_train, X_test, y_train, y_test, feat_names = transform_and_split(df_eng)
    
    # Save EVERYTHING
    np.save(os.path.join(PROCESSED_DIR, "X_train.npy"), X_train)
    np.save(os.path.join(PROCESSED_DIR, "X_test.npy"), X_test)
    np.save(os.path.join(PROCESSED_DIR, "y_train.npy"), y_train)
    np.save(os.path.join(PROCESSED_DIR, "y_test.npy"), y_test)
    
    # Save Feature Names
    with open(os.path.join(PROCESSED_DIR, "feature_names.json"), 'w') as f:
        json.dump(list(feat_names), f)
        
    print("Files Saved Successfully:")
    print(f"- X_train: {X_train.shape}")
    print(f"- X_test:  {X_test.shape}")
    print(f"- y_train: {y_train.shape}")
    print(f"- y_test:  {y_test.shape}")