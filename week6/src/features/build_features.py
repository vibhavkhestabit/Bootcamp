import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Ensure models directory exists
os.makedirs('models', exist_ok=True)

def load_data(raw_path, clean_path):
    if not os.path.exists(raw_path) or not os.path.exists(clean_path):
        raise FileNotFoundError("Missing input files. Check paths.")
    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(clean_path)
    # Recover Name for Title extraction
    clean_df['Name'] = raw_df['Name'] 
    return clean_df

def generate_features(df):
    """Applies strict feature engineering logic."""
    df = df.copy()
    
    # 1. Family Features
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
    
    # 2. Wealth/Age Interactions
    df['Fare_Per_Person'] = df['Fare'] / df['FamilySize']
    df['Age_Class'] = df['Age'] * df['Pclass']
    
    # 3. Age Categories
    df['Is_Child'] = (df['Age'] < 10).astype(int)
    df['Is_Senior'] = (df['Age'] > 60).astype(int)
    
    # 4. Title Extraction
    if 'Name' in df.columns:
        df['Title'] = df['Name'].apply(lambda x: x.split(',')[1].split('.')[0].strip())
        common_titles = ['Mr', 'Miss', 'Mrs', 'Master']
        df['Title'] = df['Title'].apply(lambda x: x if x in common_titles else 'Rare')
        df['Name_Length'] = df['Name'].apply(len)
        df = df.drop(columns=['Name']) 
    else:
        df['Title'] = 'Mr'
        df['Name_Length'] = 10

    return df

def transform_and_split(df, test_size=0.2):
    # --- STEP A: Calculate & Save Baselines (BEFORE Scaling) ---
    print("Calculating training baselines...")
    baselines = {
        "age_mean": float(df['Age'].mean()),
        "fare_mean": float(df['Fare'].mean()),
        "survival_rate": float(df['Survived'].mean())
    }
    
    with open('models/training_baselines.json', 'w') as f:
        json.dump(baselines, f, indent=4)
    print("✅ Saved models/training_baselines.json")
    # -----------------------------------------------------------

    X = df.drop(columns=['Survived'])
    y = df['Survived'].values
    
    categorical_cols = ['Sex', 'Embarked', 'Title']
    numerical_cols = ['Age', 'Fare', 'FamilySize', 'Fare_Per_Person', 'Name_Length', 'Age_Class']
    passthrough_cols = ['Pclass', 'IsAlone', 'Is_Child', 'Is_Senior']
    
    passthrough_cols = [c for c in passthrough_cols if c in X.columns]

    num_pipeline = Pipeline([('scaler', StandardScaler())])
    cat_pipeline = Pipeline([('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, numerical_cols),
            ('cat', cat_pipeline, categorical_cols),
            ('pass', 'passthrough', passthrough_cols)
        ]
    )

    print("Fitting preprocessor...")
    X_processed = preprocessor.fit_transform(X)
    
    print("Saving preprocessor object...")
    joblib.dump(preprocessor, 'models/preprocessor.pkl')

    feature_names = numerical_cols.copy()
    cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
    feature_names.extend(cat_features)
    feature_names.extend(passthrough_cols)

    print(f"Splitting data: {100*(1-test_size)}% Train, {100*test_size}% Test")
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=test_size, random_state=42)
    
    return X_train, X_test, y_train, y_test, feature_names

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_PATH = os.path.join(BASE_DIR, "data/raw/dataset.csv")
    CLEAN_PATH = os.path.join(BASE_DIR, "data/processed/final.csv")
    PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
    
    print("Starting Feature Engineering & Splitting...")
    df = load_data(RAW_PATH, CLEAN_PATH)
    df_eng = generate_features(df)
    X_train, X_test, y_train, y_test, feat_names = transform_and_split(df_eng)
    
    np.save(os.path.join(PROCESSED_DIR, "X_train.npy"), X_train)
    np.save(os.path.join(PROCESSED_DIR, "X_test.npy"), X_test)
    np.save(os.path.join(PROCESSED_DIR, "y_train.npy"), y_train)
    np.save(os.path.join(PROCESSED_DIR, "y_test.npy"), y_test)
    
    with open(os.path.join(PROCESSED_DIR, "feature_names.json"), 'w') as f:
        json.dump(list(feat_names), f)
        
    print("Files Saved Successfully.")