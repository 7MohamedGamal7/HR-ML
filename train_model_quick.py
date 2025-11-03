"""
Quick script to train the promotion prediction model
"""

import pandas as pd
from app.model_utils import build_and_train, save_model
from app.data_utils import clean_df

def main():
    print('Loading sample data...')
    df = pd.read_csv('sample_data.csv')
    print(f'Loaded {len(df)} rows')

    print('Cleaning data...')
    df = clean_df(df)
    print(f'Cleaned data: {len(df)} rows')

    print('Splitting features and target...')
    X = df.drop('promotion_eligible', axis=1)
    y = df['promotion_eligible']
    print(f'Features: {X.shape[1]} columns')
    print(f'Target distribution: {y.value_counts().to_dict()}')

    print('Training model (this may take a minute)...')
    model = build_and_train(X, y, model_type='random_forest', use_cross_validation=True)

    print('Saving model...')
    metadata = {
        'training_samples': len(X),
        'features': list(X.columns),
        'model_type': 'random_forest'
    }
    save_model(model, metadata=metadata)

    print('SUCCESS: Model trained and saved!')
    print('Location: models/promotion_model.joblib')

if __name__ == '__main__':
    main()

