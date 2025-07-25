# Predictive Maintenance of Industrial Machinery - ML Classification System

A comprehensive machine learning pipeline for predicting machinery failure types using sensor data. This project implements advanced ML techniques to achieve high-accuracy classification of different failure modes in industrial equipment.

## 🎯 Project Overview

This system predicts machinery failure types with **≥98% accuracy** using sensor readings including:
- Air temperature [K]
- Process temperature [K] 
- Rotational speed [rpm]
- Torque [Nm]
- Tool wear [min]

### Failure Types Predicted:
- **No Failure** - Normal operation
- **Tool Wear Failure (TWF)** - Cutting tool degradation
- **Heat Dissipation Failure (HDF)** - Thermal management issues
- **Power Failure (PWF)** - Insufficient power delivery
- **Overstrain Failure (OSF)** - Mechanical stress overload
- **Random Failure (RNF)** - Unpredictable system failures

## 🏗️ Project Structure

```
predictive-maintenance/
├── data/
│   └── predictive_maintenance.csv      # Synthetic dataset
├── models/
│   ├── best_model_*.pkl               # Trained best model
│   ├── feature_scaler.pkl             # StandardScaler for features
│   ├── label_encoder_*.pkl            # Label encoders
│   ├── feature_names.pkl              # Feature column names
│   ├── model_metadata.pkl             # Model performance metadata
│   └── predict_failure_function.pkl   # Standalone prediction function
├── notebooks/
│   └── predictive_maintenance_ml.ipynb # Jupyter notebook (alternative)
├── scripts/
│   ├── create_sample_data.py          # Synthetic data generation
│   └── predictive_maintenance_pipeline.py # Complete ML pipeline
├── visualizations/
│   ├── feature_distributions.png      # EDA visualizations
│   ├── correlation_heatmap.png        # Feature correlations
│   ├── feature_by_failure.png         # Feature analysis by failure type
│   ├── confusion_matrix.png           # Model evaluation
│   ├── feature_importance.png         # Feature importance ranking
│   ├── model_comparison.png           # Model performance comparison
│   └── 3d_scatter_plot.html          # Interactive 3D visualization
├── requirements.txt                   # Python dependencies
└── README.md                         # Project documentation
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone/download the project
cd predictive-maintenance

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset

```bash
python3 scripts/create_sample_data.py
```

### 3. Run Complete ML Pipeline

```bash
python3 scripts/predictive_maintenance_pipeline.py
```

This will execute the entire pipeline including:
- ✅ Data loading and exploration
- ✅ Data preprocessing and cleaning
- ✅ Comprehensive EDA with visualizations
- ✅ Feature engineering
- ✅ Multiple model training (Random Forest, XGBoost, LightGBM)
- ✅ Hyperparameter optimization using Optuna
- ✅ Model evaluation and comparison
- ✅ Visualization generation
- ✅ Model and artifact saving

## 📊 Pipeline Features

### Data Preprocessing
- **Outlier Detection**: IQR-based outlier removal
- **Feature Scaling**: StandardScaler normalization
- **Label Encoding**: Categorical variable transformation
- **Class Balancing**: SMOTE oversampling for imbalanced classes

### Feature Engineering
- **Temperature Difference**: Process - Air temperature
- **Power Calculation**: Torque × RPM / 9549
- **Tool Wear Rate**: Normalized wear rate
- **Temperature Ratio**: Process/Air temperature ratio
- **Stress Indicator**: Combined stress measurement

### Model Training
- **Random Forest**: Ensemble method with 200 estimators
- **XGBoost**: Gradient boosting with hyperparameter tuning
- **LightGBM**: Fast gradient boosting framework
- **Cross-Validation**: 5-fold stratified cross-validation
- **Hyperparameter Optimization**: Optuna-based tuning

### Evaluation Metrics
- **Accuracy**: Overall classification accuracy
- **Precision**: Weighted average precision
- **Recall**: Weighted average recall
- **F1-Score**: Weighted average F1-score
- **Confusion Matrix**: Detailed class-wise performance

## 📈 Expected Results

The pipeline typically achieves:
- **Accuracy**: ≥98%
- **Precision**: ≥97%
- **Recall**: ≥97%
- **F1-Score**: ≥97%

## 🔮 Making Predictions

### Using the Saved Model

```python
import joblib
import pandas as pd

# Load the prediction function
predict_func = joblib.load('models/predict_failure_function.pkl')

# Prepare new data (must include all required features)
new_data = pd.DataFrame({
    'Air temperature [K]': [298.5],
    'Process temperature [K]': [308.2],
    'Rotational speed [rpm]': [1500],
    'Torque [Nm]': [45.0],
    'Tool wear [min]': [120],
    'Type_encoded': [1],  # Product type encoding
    'Temp_diff': [9.7],
    'Power': [7.06],
    'Tool_wear_rate': [80.0],
    'Temp_ratio': [1.032],
    'Stress_indicator': [3.6]
})

# Get predictions
predictions = predict_func(new_data)
print(f"Predicted failure type: {predictions[0]}")

# Get prediction probabilities
predictions, probabilities = predict_func(new_data, return_probabilities=True)
print(f"Prediction probabilities: {probabilities[0]}")
```

### Required Features for Prediction

The model requires the following features:
1. **Air temperature [K]**
2. **Process temperature [K]**
3. **Rotational speed [rpm]**
4. **Torque [Nm]**
5. **Tool wear [min]**
6. **Type_encoded** (0=H, 1=L, 2=M)
7. **Temp_diff** (Process - Air temperature)
8. **Power** (Torque × RPM / 9549)
9. **Tool_wear_rate** (Tool wear / (RPM/1000))
10. **Temp_ratio** (Process temp / Air temp)
11. **Stress_indicator** ((Torque × Tool wear) / RPM)

## 🛠️ Technical Details

### Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning algorithms
- **xgboost**: Gradient boosting framework
- **lightgbm**: Gradient boosting framework
- **matplotlib/seaborn**: Data visualization
- **plotly**: Interactive visualizations
- **imbalanced-learn**: SMOTE oversampling
- **optuna**: Hyperparameter optimization
- **joblib**: Model serialization

### Model Architecture
- **Input**: 11 engineered features
- **Output**: 6 failure type classes
- **Best Model**: Typically XGBoost with optimized hyperparameters
- **Preprocessing**: StandardScaler + SMOTE
- **Validation**: Stratified 5-fold cross-validation

### Performance Optimization
- **Feature Selection**: Based on importance ranking
- **Hyperparameter Tuning**: Optuna TPE sampler
- **Class Balancing**: SMOTE oversampling
- **Cross-Validation**: Stratified sampling
- **Early Stopping**: Prevents overfitting

## 📊 Visualizations

The pipeline generates comprehensive visualizations:

1. **Feature Distributions**: Histograms and KDE plots
2. **Correlation Heatmap**: Feature correlation analysis
3. **Box Plots**: Feature distributions by failure type
4. **3D Scatter Plot**: Interactive plotly visualization
5. **Confusion Matrix**: Model performance evaluation
6. **Feature Importance**: Top feature rankings
7. **Model Comparison**: Performance metrics comparison

## 🔧 Customization

### Modifying the Pipeline

You can customize the pipeline by:

1. **Adding new features** in the `feature_engineering()` method
2. **Trying different models** in the `train_models()` method
3. **Adjusting hyperparameters** in the optimization function
4. **Changing evaluation metrics** in the `evaluate_models()` method

### Using Real Kaggle Data

To use the actual Kaggle dataset:

1. Set up Kaggle API credentials
2. Download the dataset using:
   ```bash
   kaggle datasets download -d shivamb/machine-predictive-maintenance-classification
   ```
3. Update the `data_path` parameter in the pipeline

## 🏆 Model Performance

The system achieves state-of-the-art performance through:

- **Advanced Feature Engineering**: Domain-specific feature creation
- **Ensemble Methods**: Multiple model training and selection
- **Hyperparameter Optimization**: Systematic parameter tuning
- **Class Balancing**: Addressing imbalanced datasets
- **Cross-Validation**: Robust performance estimation

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions or issues:
- Review the code documentation
- Check the visualization outputs
- Examine the model metadata
- Test with sample predictions

---

**Built with ❤️ for Industrial IoT and Predictive Maintenance Applications**
