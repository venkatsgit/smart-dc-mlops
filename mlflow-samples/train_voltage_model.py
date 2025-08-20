#!/usr/bin/env python3
"""
Local Training Script for Voltage Fluctuation Prediction
Connects to centralized MLflow server
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import requests
import time
import logging
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoltageModelTrainer:
    """Local trainer for voltage fluctuation models"""
    
    def __init__(self, mlflow_server_url, config_file=None):
        """
        Initialize voltage model trainer
        
        Args:
            mlflow_server_url: URL of centralized MLflow server
            config_file: Optional YAML config file
        """
        self.mlflow_server_url = mlflow_server_url
        self.config = self._load_config(config_file)
        
        # Connect to centralized MLflow server
        logger.info(f"Connecting to MLflow server: {mlflow_server_url}")
        mlflow.set_tracking_uri(mlflow_server_url)
        
        # Wait for server availability
        self._wait_for_mlflow_server()
        
        # Set experiment
        experiment_name = self.config.get('experiment_name', 'voltage-fluctuation-prediction')
        mlflow.set_experiment(experiment_name)
        
        logger.info(f"Using experiment: {experiment_name}")
    
    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        default_config = {
            'experiment_name': 'voltage-fluctuation-prediction',
            'model_name': 'voltage_fluctuation_predictor',
            'data_config': {
                'n_samples': 5000,
                'test_size': 0.2,
                'random_state': 42,
                'validation_split': 0.1
            },
            'model_config': {
                'random_forest': {
                    'n_estimators': 150,
                    'max_depth': 12,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42
                },
                'gradient_boosting': {
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 8,
                    'random_state': 42
                }
            },
            'training_config': {
                'cross_validation': True,
                'cv_folds': 5,
                'enable_feature_scaling': True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file {config_file}: {e}")
        
        return default_config
    
    def _wait_for_mlflow_server(self, max_wait=60):
        """Wait for MLflow server to be available"""
        logger.info("Checking MLflow server availability...")
        
        for i in range(max_wait):
            try:
                response = requests.get(f"{self.mlflow_server_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ MLflow server is ready!")
                    return True
            except requests.exceptions.RequestException:
                if i % 10 == 0:
                    logger.warning(f"Waiting for server... ({i+1}/{max_wait})")
            
            time.sleep(1)
        
        raise ConnectionError(f"❌ Could not connect to MLflow server: {self.mlflow_server_url}")
    
    def generate_voltage_data(self):
        """Generate realistic voltage fluctuation dataset"""
        logger.info("Generating voltage fluctuation dataset...")
        
        data_config = self.config['data_config']
        n_samples = data_config['n_samples']
        np.random.seed(data_config['random_state'])
        
        # Environmental and operational features
        features = {
            'temperature_celsius': np.random.normal(25, 8, n_samples),
            'humidity_percent': np.random.uniform(30, 90, n_samples),
            'electrical_load_percent': np.random.uniform(30, 95, n_samples),
            'equipment_age_years': np.random.uniform(0, 15, n_samples),
            'maintenance_days_ago': np.random.exponential(30, n_samples),
            'hour_of_day': np.random.uniform(0, 24, n_samples),
            'day_of_year': np.random.randint(1, 366, n_samples),
            'ambient_vibration': np.random.uniform(0, 10, n_samples),
            'power_factor': np.random.uniform(0.7, 1.0, n_samples)
        }
        
        # Create DataFrame
        df = pd.DataFrame(features)
        
        # Generate realistic voltage stability labels
        base_stability = np.ones(n_samples)
        
        # Temperature effects
        temp_stress = np.abs(df['temperature_celsius'] - 25) / 10
        base_stability -= temp_stress * 0.3
        
        # Load effects
        load_stress = (df['electrical_load_percent'] / 100) ** 2
        base_stability -= load_stress * 0.4
        
        # Equipment age effects
        age_stress = df['equipment_age_years'] / 15
        base_stability -= age_stress * 0.25
        
        # Peak hour effects
        peak_hours = ((df['hour_of_day'] >= 8) & (df['hour_of_day'] <= 10)) | \
                    ((df['hour_of_day'] >= 18) & (df['hour_of_day'] <= 20))
        base_stability[peak_hours] -= 0.2
        
        # Maintenance effects
        maintenance_effect = np.exp(-df['maintenance_days_ago'] / 60)
        base_stability += maintenance_effect * 0.3
        
        # Add noise
        base_stability += np.random.normal(0, 0.1, n_samples)
        
        # Convert to classification labels
        voltage_stability = np.zeros(n_samples, dtype=int)
        voltage_stability[base_stability < 0.6] = 2  # Major fluctuation
        voltage_stability[(base_stability >= 0.6) & (base_stability < 0.8)] = 1  # Minor
        voltage_stability[base_stability >= 0.8] = 0  # Stable
        
        df['voltage_stability'] = voltage_stability
        
        logger.info(f"Generated {n_samples} samples")
        logger.info(f"Class distribution: {np.bincount(voltage_stability)}")
        
        return df
    
    def train_model(self, model_type='random_forest', model_version='1.0'):
        """Train voltage fluctuation model"""
        logger.info(f"Training {model_type} model version {model_version}")
        
        # Generate data
        df = self.generate_voltage_data()
        
        # Prepare features and target
        feature_cols = [col for col in df.columns if col != 'voltage_stability']
        X = df[feature_cols]
        y = df['voltage_stability']
        
        # Split data
        data_config = self.config['data_config']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=data_config['test_size'], 
            random_state=data_config['random_state'],
            stratify=y
        )
        
        # Optional: Feature scaling
        scaler = None
        if self.config['training_config']['enable_feature_scaling']:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
        else:
            X_train_scaled = X_train
            X_test_scaled = X_test
        
        # Create model
        model_config = self.config['model_config'][model_type]
        if model_type == 'random_forest':
            model = RandomForestClassifier(**model_config)
        elif model_type == 'gradient_boosting':
            model = GradientBoostingClassifier(**model_config)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"voltage_{model_type}_v{model_version}") as run:
            # Log parameters
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("model_version", model_version)
            mlflow.log_param("training_samples", len(X_train))
            mlflow.log_param("test_samples", len(X_test))
            mlflow.log_param("n_features", len(feature_cols))
            mlflow.log_param("feature_scaling", self.config['training_config']['enable_feature_scaling'])
            
            # Log model hyperparameters
            for param, value in model_config.items():
                mlflow.log_param(f"model_{param}", value)
            
            # Train model
            start_time = time.time()
            model.fit(X_train_scaled, y_train)
            training_time = time.time() - start_time
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            if self.config['training_config']['cross_validation']:
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train, 
                    cv=self.config['training_config']['cv_folds']
                )
                mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
                mlflow.log_metric("cv_std_accuracy", cv_scores.std())
            
            # Log metrics
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("training_time_seconds", training_time)
            
            # Feature importance (for tree-based models)
            if hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(feature_cols, model.feature_importances_))
                for feature, importance in importance_dict.items():
                    mlflow.log_metric(f"feature_importance_{feature}", importance)
            
            # Log metrics and parameters only (no model artifacts to avoid permission issues)
            logger.info("Logging metrics and parameters to MLflow...")
            
            # Log additional artifacts as dictionaries (lighter than full model)
            try:
                # Classification report
                report = classification_report(y_test, y_pred, output_dict=True)
                mlflow.log_dict(report, "classification_report.json")
                
                # Confusion matrix
                cm = confusion_matrix(y_test, y_pred)
                mlflow.log_dict({"confusion_matrix": cm.tolist()}, "confusion_matrix.json")
                
                # Model metadata
                metadata = {
                    "model_type": model_type,
                    "model_version": model_version,
                    "training_timestamp": datetime.now().isoformat(),
                    "feature_columns": feature_cols,
                    "class_labels": ["Stable", "Minor Fluctuation", "Major Fluctuation"],
                    "training_config": self.config['training_config']
                }
                mlflow.log_dict(metadata, "model_metadata.json")
                
            except Exception as e:
                logger.warning(f"Could not log artifacts: {e}")
            
            # Set tags
            mlflow.set_tag("model_domain", "voltage_fluctuation")
            mlflow.set_tag("model_type", model_type)
            mlflow.set_tag("model_version", model_version)
            mlflow.set_tag("environment", "local_training")
            mlflow.set_tag("data_source", "synthetic")
            
            run_id = run.info.run_id
            
        logger.info(f"✅ Model training completed!")
        logger.info(f"📈 Accuracy: {accuracy:.4f}")
        logger.info(f"⏱️  Training time: {training_time:.2f}s")
        logger.info(f"🆔 Run ID: {run_id}")
        logger.info(f"🌐 View in MLflow: {self.mlflow_server_url}")
        
        return {
            "run_id": run_id,
            "accuracy": accuracy,
            "model_name": self.config['model_name'],
            "training_time": training_time
        }

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Local Voltage Model Training")
    parser.add_argument("--mlflow-server", required=True,
                       help="Centralized MLflow server URL")
    parser.add_argument("--model-type", choices=['random_forest', 'gradient_boosting'],
                       default='random_forest', help="Model type to train")
    parser.add_argument("--model-version", default='1.0',
                       help="Model version")
    parser.add_argument("--config", help="YAML configuration file")
    
    args = parser.parse_args()
    
    logger.info("🔋 Local Voltage Model Training")
    logger.info("=" * 40)
    logger.info(f"🔗 MLflow Server: {args.mlflow_server}")
    logger.info(f"🤖 Model Type: {args.model_type}")
    logger.info(f"🔢 Model Version: {args.model_version}")
    
    try:
        # Initialize trainer
        trainer = VoltageModelTrainer(args.mlflow_server, args.config)
        
        # Train model
        result = trainer.train_model(args.model_type, args.model_version)
        
        logger.info("🎉 Training completed successfully!")
        logger.info(f"📊 Final accuracy: {result['accuracy']:.4f}")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()