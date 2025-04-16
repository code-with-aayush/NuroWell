# model_training.py

from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import cross_val_score

def train_model(X_train, y_train):
    """
    Train an XGBoost classifier for multi-class classification.
    """
    # Initialize the model with stronger regularization
    model = XGBClassifier(
        random_state=42,
        objective='multi:softmax',
        num_class=5,
        max_depth=4,       # Slightly deeper tree to capture more complexity
        n_estimators=100,  # More trees for better learning
        gamma=0.2,         # Stronger regularization
        reg_lambda=2,      # Stronger L2 regularization
        learning_rate=0.1  # Moderate learning rate
    )
    
    # Fit the model
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test, X_train, y_train):
    """
    Evaluate the trained model on both the test set and using cross-validation.
    """
    # Predict on the test set
    y_pred = model.predict(X_test)
    
    # Print classification report and accuracy
    print("Model Evaluation Report (Test Set):")
    print(classification_report(y_test, y_pred, target_names=['Relaxed (1)', 'Low Stress (2)', 'Moderate Stress (3)', 'High Stress (4)', 'Intense Stress (5)']))
    print(f"Overall Test Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
    
    # Perform cross-validation
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"Cross-Validation Accuracy: {scores.mean() * 100:.2f}% ± {scores.std() * 100:.2f}%")