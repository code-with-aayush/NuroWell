from data_processing import load_and_preprocess_data
from model_training import train_model, evaluate_model
from real_time_prediction import predict_stress_level

def main():
    # Step 1: Data Processing
    filepath = 'synthetic_stress_data_1000.csv'  # Replace with your dataset file path
    X_train, X_test, y_train, y_test, scaler = load_and_preprocess_data(filepath)

    # Step 2: Model Training
    model = train_model(X_train, y_train)

    # Step 3: Model Evaluation
    evaluate_model(model, X_test, y_test, X_train, y_train)

    # Step 4: Real-Time Prediction on Multiple Inputs
    # Define the test data (HR, HRV, GSR, SpO2, Actual Stress Level)
    test_data = [
        (83, 43, 2.6, 98.3,1)
    ]

    print("\nTesting Model on Provided Data:")
    for i, (hr, hrv, gsr, spo2, actual_stress) in enumerate(test_data):
        predicted_stress = predict_stress_level(model, scaler, hr, hrv, gsr, spo2)
        predicted_label = ['Relaxed', 'Low Stress', 'Moderate Stress', 'High Stress', 'Intense Stress'][predicted_stress]
        actual_label = ['Relaxed', 'Low Stress', 'Moderate Stress', 'High Stress', 'Intense Stress'][actual_stress - 1]
        
        print(f"Test Case {i+1}:")
        print(f"  Input: HR={hr}, HRV={hrv}, GSR={gsr}, SpO2={spo2}")
        print(f"  Predicted Stress Level: {predicted_stress + 1} ({predicted_label})")
        print(f"  Actual Stress Level: {actual_stress} ({actual_label})")
        print(f"  Match: {'Yes' if predicted_stress + 1 == actual_stress else 'No'}\n")

if __name__ == "__main__":
    main()