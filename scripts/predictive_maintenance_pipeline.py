#!/usr/bin/env python3
"""
Predictive Maintenance of Industrial Machinery - Complete ML Pipeline
=====================================================================

This script implements a comprehensive machine learning pipeline for predicting 
machinery failure types using sensor data.

Features:
- Data loading and preprocessing
- Comprehensive EDA with visualizations
- Feature engineering
- Multiple model training (Random Forest, XGBoost, LightGBM)
- Hyperparameter optimization
- Model evaluation and comparison
- Model saving and deployment preparation

Target: ≥98% test accuracy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# Machine Learning libraries
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE

# Advanced ML models
import xgboost as xgb
import lightgbm as lgb
import optuna

# Model persistence
import joblib
import pickle

# Set style and random seed
plt.style.use('seaborn-v0_8')
np.random.seed(42)
optuna.logging.set_verbosity(optuna.logging.WARNING)

class PredictiveMaintenanceML:
    """Complete ML Pipeline for Predictive Maintenance"""
    
    def __init__(self, data_path='data/predictive_maintenance.csv'):
        self.data_path = data_path
        self.df = None
        self.df_processed = None
        self.models = {}
        self.cv_scores = {}
        self.test_results = {}
        self.best_model = None
        self.best_model_name = None
        
        # Preprocessing components
        self.scaler = None
        self.le_type = None
        self.le_failure = None
        self.feature_cols = None
        
        # Create output directories
        os.makedirs('visualizations', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        print("🚀 Predictive Maintenance ML Pipeline Initialized")
        print("=" * 60)
    
    def load_data(self):
        """Load and perform initial data exploration"""
        print("📊 Loading and exploring data...")
        
        self.df = pd.read_csv(self.data_path)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        print("\nFirst few rows:")
        print(self.df.head())
        print("\nDataset info:")
        print(self.df.info())
        print("\nBasic statistics:")
        print(self.df.describe())
        
        # Check data quality
        print(f"\nMissing values: {self.df.isnull().sum().sum()}")
        print(f"Duplicate rows: {self.df.duplicated().sum()}")
        print("\nFailure Type Distribution:")
        print(self.df['Failure Type'].value_counts())
        
        return self
    
    def preprocess_data(self):
        """Clean and preprocess the data"""
        print("\n🔧 Preprocessing data...")
        
        # Create a copy for preprocessing
        self.df_processed = self.df.copy()
        
        # Remove unnecessary columns
        columns_to_drop = ['UDI', 'Product ID']
        self.df_processed = self.df_processed.drop(columns=columns_to_drop)
        
        # Handle outliers using IQR method
        numerical_cols = ['Air temperature [K]', 'Process temperature [K]', 
                         'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
        
        outlier_indices = set()
        for col in numerical_cols:
            Q1 = self.df_processed[col].quantile(0.25)
            Q3 = self.df_processed[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df_processed[(self.df_processed[col] < lower_bound) | 
                                       (self.df_processed[col] > upper_bound)].index
            outlier_indices.update(outliers)
        
        print(f"Removing {len(outlier_indices)} outlier rows...")
        self.df_processed = self.df_processed.drop(outlier_indices)
        
        # Encode categorical variables
        self.le_type = LabelEncoder()
        self.df_processed['Type_encoded'] = self.le_type.fit_transform(self.df_processed['Type'])
        
        self.le_failure = LabelEncoder()
        self.df_processed['Failure_Type_encoded'] = self.le_failure.fit_transform(self.df_processed['Failure Type'])
        
        print(f"Shape after preprocessing: {self.df_processed.shape}")
        print(f"Type classes: {dict(zip(self.le_type.classes_, self.le_type.transform(self.le_type.classes_)))}")
        print(f"Failure classes: {dict(zip(self.le_failure.classes_, self.le_failure.transform(self.le_failure.classes_)))}")
        
        return self
    
    def exploratory_data_analysis(self):
        """Perform comprehensive EDA with visualizations"""
        print("\n📈 Performing Exploratory Data Analysis...")
        
        numerical_cols = ['Air temperature [K]', 'Process temperature [K]', 
                         'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
        
        # 1. Distribution plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, col in enumerate(numerical_cols):
            sns.histplot(data=self.df_processed, x=col, kde=True, ax=axes[i])
            axes[i].set_title(f'Distribution of {col}')
            axes[i].tick_params(axis='x', rotation=45)
        
        # Failure type distribution
        failure_counts = self.df_processed['Failure Type'].value_counts()
        axes[5].pie(failure_counts.values, labels=failure_counts.index, autopct='%1.1f%%')
        axes[5].set_title('Failure Type Distribution')
        
        plt.tight_layout()
        plt.savefig('visualizations/feature_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Correlation heatmap
        plt.figure(figsize=(12, 10))
        correlation_cols = numerical_cols + ['Type_encoded', 'Machine failure', 'Failure_Type_encoded']
        correlation_matrix = self.df_processed[correlation_cols].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                    square=True, linewidths=0.5)
        plt.title('Feature Correlation Heatmap')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('visualizations/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 3. Box plots by failure type
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, col in enumerate(numerical_cols):
            sns.boxplot(data=self.df_processed, x='Machine failure', y=col, ax=axes[i])
            axes[i].set_title(f'{col} by Machine Failure')
        
        # Product type distribution
        type_counts = self.df_processed['Type'].value_counts()
        axes[5].bar(type_counts.index, type_counts.values)
        axes[5].set_title('Product Type Distribution')
        
        plt.tight_layout()
        plt.savefig('visualizations/feature_by_failure.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 4. Interactive 3D plot with Plotly
        fig = px.scatter_3d(self.df_processed, 
                            x='Air temperature [K]', 
                            y='Process temperature [K]', 
                            z='Torque [Nm]',
                            color='Failure Type',
                            title='3D Scatter: Temperature vs Torque by Failure Type',
                            opacity=0.7)
        fig.write_html('visualizations/3d_scatter_plot.html')
        print("3D interactive plot saved as HTML")
        
        return self
    
    def feature_engineering(self):
        """Create engineered features"""
        print("\n⚙️ Engineering features...")
        
        # Create engineered features
        self.df_processed['Temp_diff'] = (self.df_processed['Process temperature [K]'] - 
                                         self.df_processed['Air temperature [K]'])
        
        self.df_processed['Power'] = (self.df_processed['Torque [Nm]'] * 
                                     self.df_processed['Rotational speed [rpm]'] / 9549)
        
        self.df_processed['Tool_wear_rate'] = (self.df_processed['Tool wear [min]'] / 
                                              (self.df_processed['Rotational speed [rpm]'] / 1000))
        
        self.df_processed['Temp_ratio'] = (self.df_processed['Process temperature [K]'] / 
                                          self.df_processed['Air temperature [K]'])
        
        self.df_processed['Stress_indicator'] = ((self.df_processed['Torque [Nm]'] * 
                                                 self.df_processed['Tool wear [min]']) / 
                                                self.df_processed['Rotational speed [rpm]'])
        
        # Define all feature columns
        numerical_cols = ['Air temperature [K]', 'Process temperature [K]', 
                         'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
        new_features = ['Temp_diff', 'Power', 'Tool_wear_rate', 'Temp_ratio', 'Stress_indicator']
        self.feature_cols = numerical_cols + ['Type_encoded'] + new_features
        
        print(f"Total features after engineering: {len(self.feature_cols)}")
        print("New features statistics:")
        print(self.df_processed[new_features].describe())
        
        return self
    
    def prepare_data_for_modeling(self):
        """Prepare final datasets for modeling"""
        print("\n📋 Preparing data for modeling...")
        
        # Prepare features and target
        X = self.df_processed[self.feature_cols]
        y = self.df_processed['Failure_Type_encoded']  # Multiclass classification
        
        print(f"Feature matrix shape: {X.shape}")
        print(f"Class distribution: {pd.Series(y).value_counts().to_dict()}")
        
        # Apply SMOTE for class balancing (with k_neighbors adjustment for small classes)
        # Find the minimum class size
        class_counts = pd.Series(y).value_counts()
        min_class_size = class_counts.min()
        
        if min_class_size < 6:  # SMOTE default k_neighbors is 5, so minimum needed is 6
            # Use BorderlineSMOTE with smaller k_neighbors or skip SMOTE for very small classes
            from imblearn.over_sampling import BorderlineSMOTE
            k_neighbors = min(min_class_size - 1, 3) if min_class_size > 3 else 1
            smote = BorderlineSMOTE(random_state=42, k_neighbors=k_neighbors)
            try:
                X_balanced, y_balanced = smote.fit_resample(X, y)
            except ValueError:
                # If still failing, use ADASYN or skip balancing
                print(f"Warning: Skipping SMOTE due to very small classes. Using original data.")
                X_balanced, y_balanced = X, y
        else:
            smote = SMOTE(random_state=42)
            X_balanced, y_balanced = smote.fit_resample(X, y)
        
        print(f"After SMOTE - Shape: {X_balanced.shape}")
        print(f"After SMOTE - Class distribution: {pd.Series(y_balanced).value_counts().to_dict()}")
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
        )
        
        # Feature scaling
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"Training set shape: {self.X_train_scaled.shape}")
        print(f"Test set shape: {self.X_test_scaled.shape}")
        
        return self
    
    def train_models(self):
        """Train multiple ML models"""
        print("\n🤖 Training ML models...")
        
        # Stratified K-Fold cross-validation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # 1. Random Forest
        print("Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        rf_scores = cross_val_score(rf_model, self.X_train_scaled, self.y_train, 
                                   cv=skf, scoring='accuracy')
        self.models['Random Forest'] = rf_model
        self.cv_scores['Random Forest'] = rf_scores
        print(f"Random Forest CV Accuracy: {rf_scores.mean():.4f} (+/- {rf_scores.std() * 2:.4f})")
        
        # 2. XGBoost
        print("Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            eval_metric='mlogloss'
        )
        xgb_scores = cross_val_score(xgb_model, self.X_train_scaled, self.y_train,
                                    cv=skf, scoring='accuracy')
        self.models['XGBoost'] = xgb_model
        self.cv_scores['XGBoost'] = xgb_scores
        print(f"XGBoost CV Accuracy: {xgb_scores.mean():.4f} (+/- {xgb_scores.std() * 2:.4f})")
        
        # 3. LightGBM
        print("Training LightGBM...")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbose=-1
        )
        lgb_scores = cross_val_score(lgb_model, self.X_train_scaled, self.y_train,
                                    cv=skf, scoring='accuracy')
        self.models['LightGBM'] = lgb_model
        self.cv_scores['LightGBM'] = lgb_scores
        print(f"LightGBM CV Accuracy: {lgb_scores.mean():.4f} (+/- {lgb_scores.std() * 2:.4f})")
        
        # Train all models on full training set
        print("Training models on full training set...")
        for name, model in self.models.items():
            model.fit(self.X_train_scaled, self.y_train)
        
        return self
    
    def optimize_best_model(self):
        """Hyperparameter optimization using Optuna"""
        print("\n🔍 Performing hyperparameter optimization...")
        
        # Find best CV model
        best_cv_model = max(self.cv_scores.items(), key=lambda x: x[1].mean())
        print(f"Best CV model: {best_cv_model[0]} with accuracy: {best_cv_model[1].mean():.4f}")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'random_state': 42,
                'eval_metric': 'mlogloss'
            }
            
            model = xgb.XGBClassifier(**params)
            scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=3, scoring='accuracy')
            return scores.mean()
        
        # Run optimization
        study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(objective, n_trials=50)
        
        print(f"Best trial accuracy: {study.best_value:.4f}")
        print(f"Best parameters: {study.best_params}")
        
        # Train optimized model
        best_xgb_model = xgb.XGBClassifier(**study.best_params)
        best_xgb_model.fit(self.X_train_scaled, self.y_train)
        self.models['XGBoost_Optimized'] = best_xgb_model
        
        return self
    
    def evaluate_models(self):
        """Evaluate all models on test set"""
        print("\n📊 Evaluating models on test set...")
        
        for name, model in self.models.items():
            # Predictions
            y_pred = model.predict(self.X_test_scaled)
            y_pred_proba = model.predict_proba(self.X_test_scaled)
            
            # Metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred, average='weighted')
            f1 = f1_score(self.y_test, y_pred, average='weighted')
            
            self.test_results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            print(f"\n{name} Results:")
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Results summary
        results_df = pd.DataFrame(self.test_results).T
        results_df = results_df.drop(['predictions', 'probabilities'], axis=1)
        
        print("\n" + "="*60)
        print("MODEL COMPARISON SUMMARY")
        print("="*60)
        print(results_df.round(4))
        
        # Select best model
        self.best_model_name = results_df['accuracy'].idxmax()
        self.best_model = self.models[self.best_model_name]
        best_accuracy = results_df.loc[self.best_model_name, 'accuracy']
        
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"🎯 Best Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
        
        return self
    
    def create_visualizations(self):
        """Create evaluation visualizations"""
        print("\n📈 Creating evaluation visualizations...")
        
        best_predictions = self.test_results[self.best_model_name]['predictions']
        
        # 1. Confusion Matrix
        plt.figure(figsize=(10, 8))
        cm = confusion_matrix(self.y_test, best_predictions)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.le_failure.classes_,
                    yticklabels=self.le_failure.classes_)
        plt.title(f'Confusion Matrix - {self.best_model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('visualizations/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Feature importance
        if hasattr(self.best_model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_cols,
                'importance': self.best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            plt.figure(figsize=(12, 8))
            sns.barplot(data=feature_importance.head(10), x='importance', y='feature')
            plt.title(f'Top 10 Feature Importance - {self.best_model_name}')
            plt.xlabel('Importance Score')
            plt.tight_layout()
            plt.savefig('visualizations/feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 3. Model comparison
        results_df = pd.DataFrame(self.test_results).T.drop(['predictions', 'probabilities'], axis=1)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Accuracy comparison
        model_names = list(results_df.index)
        accuracies = results_df['accuracy'].values
        
        bars1 = axes[0].bar(model_names, accuracies, 
                           color=['skyblue', 'lightgreen', 'lightcoral', 'gold'][:len(model_names)])
        axes[0].set_title('Model Accuracy Comparison')
        axes[0].set_ylabel('Accuracy')
        axes[0].set_ylim(0.9, 1.0)
        axes[0].tick_params(axis='x', rotation=45)
        
        for bar, acc in zip(bars1, accuracies):
            axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f'{acc:.4f}', ha='center', va='bottom')
        
        # F1-Score comparison
        f1_scores = results_df['f1_score'].values
        bars2 = axes[1].bar(model_names, f1_scores,
                           color=['skyblue', 'lightgreen', 'lightcoral', 'gold'][:len(model_names)])
        axes[1].set_title('Model F1-Score Comparison')
        axes[1].set_ylabel('F1-Score')
        axes[1].set_ylim(0.9, 1.0)
        axes[1].tick_params(axis='x', rotation=45)
        
        for bar, f1 in zip(bars2, f1_scores):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f'{f1:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('visualizations/model_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self
    
    def save_models_and_artifacts(self):
        """Save trained models and preprocessing artifacts"""
        print("\n💾 Saving models and artifacts...")
        
        # Save the best model
        model_filename = f'models/best_model_{self.best_model_name.lower().replace(" ", "_")}.pkl'
        joblib.dump(self.best_model, model_filename)
        print(f"✅ Best model saved: {model_filename}")
        
        # Save preprocessing components
        joblib.dump(self.scaler, 'models/feature_scaler.pkl')
        joblib.dump(self.le_type, 'models/label_encoder_type.pkl')
        joblib.dump(self.le_failure, 'models/label_encoder_failure.pkl')
        joblib.dump(self.feature_cols, 'models/feature_names.pkl')
        
        # Save model metadata
        results_df = pd.DataFrame(self.test_results).T.drop(['predictions', 'probabilities'], axis=1)
        metadata = {
            'best_model_name': self.best_model_name,
            'accuracy': results_df.loc[self.best_model_name, 'accuracy'],
            'precision': results_df.loc[self.best_model_name, 'precision'],
            'recall': results_df.loc[self.best_model_name, 'recall'],
            'f1_score': results_df.loc[self.best_model_name, 'f1_score'],
            'feature_names': self.feature_cols,
            'target_classes': self.le_failure.classes_.tolist(),
            'training_date': datetime.now().isoformat(),
            'dataset_shape': self.df.shape
        }
        
        joblib.dump(metadata, 'models/model_metadata.pkl')
        print("✅ All artifacts saved successfully!")
        
        return self
    
    def create_prediction_function(self):
        """Create a standalone prediction function"""
        print("\n🔮 Creating prediction function...")
        
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
            model = joblib.load(f'{model_path}best_model_{self.best_model_name.lower().replace(" ", "_")}.pkl')
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
        
        # Save prediction function as a separate script instead of pickle
        prediction_script = f'''import joblib
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
    model = joblib.load(f'{{model_path}}best_model_{self.best_model_name.lower().replace(" ", "_")}.pkl')
    scaler = joblib.load(f'{{model_path}}feature_scaler.pkl')
    le_failure = joblib.load(f'{{model_path}}label_encoder_failure.pkl')
    feature_names = joblib.load(f'{{model_path}}feature_names.pkl')
    
    # Validate features
    missing_features = set(feature_names) - set(new_data.columns)
    if missing_features:
        raise ValueError(f"Missing features: {{missing_features}}")
    
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
'''
        
        with open('models/predict_failure.py', 'w') as f:
            f.write(prediction_script)
        print("✅ Prediction function saved as script!")
        
        return predict_failure
    
    def run_complete_pipeline(self):
        """Run the complete ML pipeline"""
        print("🚀 Starting Complete Predictive Maintenance ML Pipeline")
        print("=" * 80)
        
        try:
            (self.load_data()
             .preprocess_data()
             .exploratory_data_analysis()
             .feature_engineering()
             .prepare_data_for_modeling()
             .train_models()
             .optimize_best_model()
             .evaluate_models()
             .create_visualizations()
             .save_models_and_artifacts())
            
            predict_func = self.create_prediction_function()
            
            # Final summary
            results_df = pd.DataFrame(self.test_results).T.drop(['predictions', 'probabilities'], axis=1)
            best_accuracy = results_df.loc[self.best_model_name, 'accuracy']
            
            print("\n" + "=" * 80)
            print("🎉 PREDICTIVE MAINTENANCE MODEL TRAINING COMPLETE!")
            print("=" * 80)
            print(f"✅ Best Model: {self.best_model_name}")
            print(f"✅ Test Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
            print(f"✅ F1-Score: {results_df.loc[self.best_model_name, 'f1_score']:.4f}")
            print(f"✅ Precision: {results_df.loc[self.best_model_name, 'precision']:.4f}")
            print(f"✅ Recall: {results_df.loc[self.best_model_name, 'recall']:.4f}")
            print(f"\n📊 Dataset Size: {self.df.shape[0]:,} samples")
            print(f"📊 Features Used: {len(self.feature_cols)}")
            print(f"📊 Failure Types: {len(self.le_failure.classes_)}")
            print(f"\n💾 Models saved in: models/")
            print(f"📈 Visualizations saved in: visualizations/")
            
            # Check target achievement
            target_accuracy = 0.98
            if best_accuracy >= target_accuracy:
                print(f"\n🎯 TARGET ACHIEVED! Model accuracy ({best_accuracy:.4f}) exceeds target ({target_accuracy:.4f})")
            else:
                print(f"\n⚠️  Target not achieved: Model accuracy ({best_accuracy:.4f}) below target ({target_accuracy:.4f})")
            
            print("\n" + "=" * 80)
            
            return self
            
        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {str(e)}")
            raise

def main():
    """Main execution function"""
    # Initialize and run pipeline
    pipeline = PredictiveMaintenanceML('data/predictive_maintenance.csv')
    pipeline.run_complete_pipeline()
    
    # Test the saved model
    print("\n🧪 Testing saved model with sample predictions...")
    
    # Load prediction function and test
    import sys
    sys.path.append('models')
    from predict_failure import predict_failure
    predict_func = predict_failure
    
    # Create test sample
    sample_data = pipeline.X_test.iloc[:3].copy()
    actual_labels = pipeline.le_failure.inverse_transform(pipeline.y_test[:3])
    
    try:
        predicted_labels, predicted_probs = predict_func(sample_data, return_probabilities=True)
        
        print("\nSample Predictions:")
        for i, (actual, predicted) in enumerate(zip(actual_labels, predicted_labels)):
            print(f"  Sample {i+1}: Actual = {actual}, Predicted = {predicted}")
            prob_dict = dict(zip(pipeline.le_failure.classes_, predicted_probs[i]))
            print(f"    Probabilities: {prob_dict}")
    
    except Exception as e:
        print(f"Prediction test failed: {str(e)}")
    
    print("\n✨ Pipeline execution completed successfully!")

if __name__ == "__main__":
    main()