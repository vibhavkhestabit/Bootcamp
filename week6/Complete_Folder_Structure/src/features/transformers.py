from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np

class TitanicFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self 

    def transform(self, X, y=None):
        df = X.copy()
        
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