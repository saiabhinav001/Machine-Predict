import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
import os

# Set random seed for reproducibility
np.random.seed(42)

def create_synthetic_maintenance_data(n_samples=10000):
    """
    Create synthetic predictive maintenance data similar to the Kaggle dataset
    """
    
    # Generate base features
    data = {}
    
    # Product ID (categorical)
    product_types = ['L', 'M', 'H']  # Low, Medium, High quality variants
    data['Type'] = np.random.choice(product_types, n_samples, p=[0.6, 0.3, 0.1])
    
    # Air temperature [K]
    data['Air temperature [K]'] = np.random.normal(298.1, 2.0, n_samples)
    
    # Process temperature [K] 
    data['Process temperature [K]'] = data['Air temperature [K]'] + np.random.normal(10, 1.5, n_samples)
    
    # Rotational speed [rpm]
    data['Rotational speed [rpm]'] = np.random.normal(1538.8, 179.3, n_samples)
    
    # Torque [Nm]
    data['Torque [Nm]'] = np.random.normal(40.17, 9.97, n_samples)
    
    # Tool wear [min]
    data['Tool wear [min]'] = np.random.exponential(108, n_samples)
    
    # Create failure conditions based on realistic scenarios
    failures = []
    failure_types = []
    
    for i in range(n_samples):
        failure = 0
        failure_type = 'No Failure'
        
        # Tool Wear Failure (TWF)
        if data['Tool wear [min]'][i] > 200 and np.random.random() < 0.7:
            failure = 1
            failure_type = 'Tool Wear Failure'
        
        # Heat Dissipation Failure (HDF)
        elif (data['Air temperature [K]'][i] > 300 and 
              data['Process temperature [K]'][i] > 310 and 
              np.random.random() < 0.6):
            failure = 1
            failure_type = 'Heat Dissipation Failure'
        
        # Power Failure (PWF)
        elif (data['Torque [Nm]'][i] > 60 and 
              data['Rotational speed [rpm]'][i] < 1200 and 
              np.random.random() < 0.5):
            failure = 1
            failure_type = 'Power Failure'
        
        # Overstrain Failure (OSF)
        elif (data['Torque [Nm]'][i] > 55 and 
              data['Tool wear [min]'][i] > 150 and 
              np.random.random() < 0.4):
            failure = 1
            failure_type = 'Overstrain Failure'
        
        # Random Failure (RNF)
        elif np.random.random() < 0.01:
            failure = 1
            failure_type = 'Random Failure'
        
        failures.append(failure)
        failure_types.append(failure_type)
    
    # Add machine failure and failure type columns
    data['Machine failure'] = failures
    data['Failure Type'] = failure_types
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add UDI (Unique identifier)
    df.insert(0, 'UDI', range(1, len(df) + 1))
    
    # Add Product ID
    df.insert(1, 'Product ID', [f"{row['Type']}{str(row['UDI']).zfill(5)}" for _, row in df.iterrows()])
    
    return df

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate synthetic data
    print("Generating synthetic predictive maintenance data...")
    df = create_synthetic_maintenance_data(10000)
    
    # Save to CSV
    output_path = 'data/predictive_maintenance.csv'
    df.to_csv(output_path, index=False)
    
    print(f"Dataset created and saved to {output_path}")
    print(f"Dataset shape: {df.shape}")
    print("\nDataset info:")
    print(df.info())
    print("\nFailure type distribution:")
    print(df['Failure Type'].value_counts())
    print("\nFirst few rows:")
    print(df.head())

if __name__ == "__main__":
    main()