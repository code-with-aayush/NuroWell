# data_processing.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(filepath):
    """
    Load the dataset, preprocess it, and split into training and testing sets.
    """
    # Load dataset
    data = pd.read_csv(filepath)
    
    # Features and labels
    X = data[['HR (bpm)', 'HRV (ms)', 'GSR (µS)', 'SpO2 (%)']].values  # Convert to NumPy array
    y = data['Stress Level (1-5)'] - 1  # Shift labels from [1, 2, 3, 4, 5] to [0, 1, 2, 3, 4]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test, scaler