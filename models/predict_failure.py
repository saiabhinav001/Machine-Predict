import joblib
import pandas as pd

def predict_failure(new_data, model_path='models/', return_probabilities=False):
    """
    Predict machinery failure type for new data
    
    Parameters:
    new_data: pandas DataFrame with required features
    model_path: path to saved models
    return_probabilities: whether to return prediction probabilities
    
    Returns:
    predictions and optionally probabilities
    """
    # Load components
    model = joblib.load(f'{model_path}best_model_xgboost.pkl')
    scaler = joblib.load(f'{model_path}feature_scaler.pkl')
    le_failure = joblib.load(f'{model_path}label_encoder_failure.pkl')
    feature_names = joblib.load(f'{model_path}feature_names.pkl')
    
    # Validate features
    missing_features = set(feature_names) - set(new_data.columns)
    if missing_features:
        raise ValueError(f"Missing features: {missing_features}")
    
    # Prepare data
    X_new = new_data[feature_names]
    X_new_scaled = scaler.transform(X_new)
    
    # Make predictions
    predictions_encoded = model.predict(X_new_scaled)
    predictions = le_failure.inverse_transform(predictions_encoded)
    
    if return_probabilities:
        probabilities = model.predict_proba(X_new_scaled)
        return predictions, probabilities
    
    return predictions
