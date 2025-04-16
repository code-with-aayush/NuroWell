# real_time_prediction.py

def predict_stress_level(model, scaler, hr, hrv, gsr, spo2):
    """
    Predict stress level in real-time using the trained model.
    """
    # Prepare input data
    input_data = [[hr, hrv, gsr, spo2]]
    input_data_scaled = scaler.transform(input_data)  # Scale the input data
    
    # Debugging: Print scaled input data
    print(f"Scaled Input Data: {input_data_scaled}")
    
    # Predict stress level
    prediction = model.predict(input_data_scaled)[0]
    return int(prediction)  # Ensure the prediction is an integer