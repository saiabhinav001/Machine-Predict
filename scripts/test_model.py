#!/usr/bin/env python3
"""
Test Script for Predictive Maintenance Model
============================================

This script demonstrates how to use the trained predictive maintenance model
for making predictions on new machinery sensor data.
"""

import sys
import os
sys.path.append('models')

import pandas as pd
import numpy as np
from predict_failure import predict_failure

def test_single_prediction():
    """Test prediction with a single data point"""
    print("🔧 Testing Single Prediction...")
    
    # Create sample sensor data
    sample_data = pd.DataFrame({
        'Air temperature [K]': [300.5],
        'Process temperature [K]': [312.3],
        'Rotational speed [rpm]': [1200],
        'Torque [Nm]': [65.0],
        'Tool wear [min]': [220],
        'Type_encoded': [1],  # L type product
        'Temp_diff': [11.8],
        'Power': [8.17],
        'Tool_wear_rate': [183.33],
        'Temp_ratio': [1.039],
        'Stress_indicator': [12.0]
    })
    
    # Get prediction
    prediction = predict_failure(sample_data)
    print(f"Predicted failure type: {prediction[0]}")
    
    # Get prediction with probabilities
    prediction, probabilities = predict_failure(sample_data, return_probabilities=True)
    print(f"Prediction: {prediction[0]}")
    print(f"Probabilities:")
    
    # Load label encoder to get class names
    import joblib
    le_failure = joblib.load('models/label_encoder_failure.pkl')
    
    for class_name, prob in zip(le_failure.classes_, probabilities[0]):
        print(f"  {class_name}: {prob:.4f}")

def test_batch_predictions():
    """Test predictions with multiple data points"""
    print("\n📊 Testing Batch Predictions...")
    
    # Create multiple sensor readings
    batch_data = pd.DataFrame({
        'Air temperature [K]': [298.1, 302.5, 295.3],
        'Process temperature [K]': [308.4, 315.2, 305.8],
        'Rotational speed [rpm]': [1550, 1100, 1600],
        'Torque [Nm]': [42.0, 68.5, 38.2],
        'Tool wear [min]': [90, 250, 45],
        'Type_encoded': [1, 0, 2],  # Different product types
        'Temp_diff': [10.3, 12.7, 10.5],
        'Power': [6.79, 7.88, 6.38],
        'Tool_wear_rate': [58.06, 227.27, 28.13],
        'Temp_ratio': [1.035, 1.041, 1.036],
        'Stress_indicator': [2.42, 15.45, 1.08]
    })
    
    # Get predictions
    predictions = predict_failure(batch_data)
    
    print(f"Batch predictions:")
    for i, pred in enumerate(predictions):
        print(f"  Sample {i+1}: {pred}")

def generate_test_features(air_temp, process_temp, rpm, torque, tool_wear, product_type=1):
    """
    Helper function to generate all required features from basic sensor readings
    
    Parameters:
    air_temp: Air temperature in Kelvin
    process_temp: Process temperature in Kelvin
    rpm: Rotational speed in RPM
    torque: Torque in Nm
    tool_wear: Tool wear in minutes
    product_type: Product type (0=H, 1=L, 2=M)
    
    Returns:
    DataFrame with all required features
    """
    data = pd.DataFrame({
        'Air temperature [K]': [air_temp],
        'Process temperature [K]': [process_temp],
        'Rotational speed [rpm]': [rpm],
        'Torque [Nm]': [torque],
        'Tool wear [min]': [tool_wear],
        'Type_encoded': [product_type],
        'Temp_diff': [process_temp - air_temp],
        'Power': [torque * rpm / 9549],
        'Tool_wear_rate': [tool_wear / (rpm / 1000)],
        'Temp_ratio': [process_temp / air_temp],
        'Stress_indicator': [(torque * tool_wear) / rpm]
    })
    return data

def test_different_scenarios():
    """Test predictions for different failure scenarios"""
    print("\n🎯 Testing Different Failure Scenarios...")
    
    scenarios = [
        {
            'name': 'Normal Operation',
            'air_temp': 298.0,
            'process_temp': 308.0,
            'rpm': 1500,
            'torque': 40.0,
            'tool_wear': 80
        },
        {
            'name': 'High Temperature (Heat Dissipation Risk)',
            'air_temp': 302.0,
            'process_temp': 315.0,
            'rpm': 1500,
            'torque': 40.0,
            'tool_wear': 80
        },
        {
            'name': 'High Tool Wear (Tool Wear Failure Risk)',
            'air_temp': 298.0,
            'process_temp': 308.0,
            'rpm': 1500,
            'torque': 40.0,
            'tool_wear': 250
        },
        {
            'name': 'High Torque + Low RPM (Power Failure Risk)',
            'air_temp': 298.0,
            'process_temp': 308.0,
            'rpm': 1000,
            'torque': 70.0,
            'tool_wear': 80
        },
        {
            'name': 'High Stress (Overstrain Risk)',
            'air_temp': 298.0,
            'process_temp': 308.0,
            'rpm': 1500,
            'torque': 60.0,
            'tool_wear': 200
        }
    ]
    
    for scenario in scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        data = generate_test_features(
            scenario['air_temp'],
            scenario['process_temp'],
            scenario['rpm'],
            scenario['torque'],
            scenario['tool_wear']
        )
        
        prediction = predict_failure(data)
        print(f"    Prediction: {prediction[0]}")

def main():
    """Main function to run all tests"""
    print("🚀 Predictive Maintenance Model Testing")
    print("=" * 50)
    
    try:
        test_single_prediction()
        test_batch_predictions()
        test_different_scenarios()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n💡 Usage Tips:")
        print("  - Ensure all 11 features are provided")
        print("  - Features must be in correct units (K for temperature, rpm, Nm, minutes)")
        print("  - Type_encoded: 0=H, 1=L, 2=M")
        print("  - Use generate_test_features() helper for easy feature generation")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("Make sure the model files are present in the models/ directory")

if __name__ == "__main__":
    main()