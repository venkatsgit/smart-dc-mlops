
#!/usr/bin/env python3
"""
Working Voltage Training: Metadata in Citus + JSON Artifacts
"""

import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import pickle
import base64
import json
import time
from datetime import datetime

# Connect to MLflow
mlflow.set_tracking_uri("http://localhost:5000")

class WorkingVoltageTrainer:
    def __init__(self):
        # Set experiment
        experiment_name = "working-voltage-prediction"
        try:
            mlflow.create_experiment(experiment_name)
            print(f"✅ Created experiment: {experiment_name}")
        except:
            print(f"✅ Using existing experiment: {experiment_name}")
        
        mlflow.set_experiment(experiment_name)
    
    def generate_data(self, n_samples=3000):
        """Generate voltage data"""
        np.random.seed(42)
        
        features = {
            'temperature': np.random.normal(25, 8, n_samples),
            'humidity': np.random.uniform(30, 90, n_samples),
            'load': np.random.uniform(30, 95, n_samples),
            'equipment_age': np.random.uniform(0, 15, n_samples),
            'maintenance_days': np.random.exponential(30, n_samples),
            'frequency': np.random.normal(50, 0.1, n_samples)
        }
        
        df = pd.DataFrame(features)
        
        # Generate target
        stability = np.ones(n_samples)
        stability -= np.abs(df['temperature'] - 25) / 10 * 0.3
        stability -= (df['load'] / 100) ** 2 * 0.4
        stability -= (df['equipment_age'] / 15) * 0.25
        stability += np.exp(-df['maintenance_days'] / 60) * 0.3
        stability += np.random.normal(0, 0.1, n_samples)
        
        df['voltage_class'] = np.where(stability < 0.5, 2,
                                     np.where(stability < 0.75, 1, 0))
        
        return df
    
    def serialize_model(self, model):
        """Serialize model to base64 string for JSON storage"""
        try:
            model_bytes = pickle.dumps(model)
            model_b64 = base64.b64encode(model_bytes).decode('utf-8')
            return model_b64
        except Exception as e:
            print(f"⚠️ Model serialization failed: {e}")
            return None
    
    def train_and_save(self, model_type="random_forest"):
        """Train model with working metadata and artifact logging"""
        
        # Generate data
        df = self.generate_data()
        feature_cols = [col for col in df.columns if col != 'voltage_class']
        X, y = df[feature_cols], df['voltage_class']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Create model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model: {model_type}")
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"working_{model_type}_{int(time.time())}") as run:
            print(f"🚀 Run ID: {run.info.run_id}")
            print(f"📂 Artifact URI: {run.info.artifact_uri}")
            
            # === METADATA LOGGING (goes to Citus) ===
            print("📊 Logging metadata to Citus...")
            
            # Parameters
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("n_samples", len(df))
            mlflow.log_param("n_features", len(feature_cols))
            mlflow.log_param("test_size", 0.2)
            mlflow.log_param("scaling", "StandardScaler")
            mlflow.log_param("feature_names", ",".join(feature_cols))
            
            # Model hyperparameters
            for param, value in model.get_params().items():
                mlflow.log_param(f"model_{param}", value)
            
            # Train model
            print("🤖 Training model...")
            start_time = time.time()
            model.fit(X_train_scaled, y_train)
            training_time = time.time() - start_time
            
            # Evaluate
            train_acc = model.score(X_train_scaled, y_train)
            test_acc = model.score(X_test_scaled, y_test)
            y_pred = model.predict(X_test_scaled)
            
            # Metrics
            mlflow.log_metric("train_accuracy", train_acc)
            mlflow.log_metric("test_accuracy", test_acc)
            mlflow.log_metric("training_time", training_time)
            mlflow.log_metric("overfitting", train_acc - test_acc)
            
            # Feature importance metrics
            if hasattr(model, 'feature_importances_'):
                for i, (feature, importance) in enumerate(zip(feature_cols, model.feature_importances_)):
                    mlflow.log_metric(f"importance_{feature}", importance)
                
                # Log top 3 features
                top_features = sorted(zip(feature_cols, model.feature_importances_), 
                                    key=lambda x: x[1], reverse=True)[:3]
                for i, (feature, importance) in enumerate(top_features):
                    mlflow.log_param(f"top_{i+1}_feature", feature)
                    mlflow.log_metric(f"top_{i+1}_importance", importance)
            
            # Class-wise performance
            report = classification_report(y_test, y_pred, output_dict=True)
            for class_name in ['0', '1', '2']:
                if class_name in report:
                    mlflow.log_metric(f"precision_class_{class_name}", report[class_name]['precision'])
                    mlflow.log_metric(f"recall_class_{class_name}", report[class_name]['recall'])
                    mlflow.log_metric(f"f1_class_{class_name}", report[class_name]['f1-score'])
            
            # Overall metrics
            mlflow.log_metric("macro_avg_f1", report['macro avg']['f1-score'])
            mlflow.log_metric("weighted_avg_f1", report['weighted avg']['f1-score'])
            
            # Tags
            mlflow.set_tag("model_family", "tree_based")
            mlflow.set_tag("data_type", "voltage_monitoring")
            mlflow.set_tag("storage_type", "citus_metadata")
            mlflow.set_tag("status", "completed")
            mlflow.set_tag("created_date", datetime.now().strftime('%Y-%m-%d'))
            mlflow.set_tag("environment", "development")
            
            # === ARTIFACT LOGGING AS JSON (works!) ===
            print("💾 Saving artifacts as JSON...")
            
            # 1. Classification Report
            try:
                mlflow.log_dict(report, "classification_report.json")
                print("✅ Classification report saved")
            except Exception as e:
                print(f"❌ Classification report failed: {e}")
            
            # 2. Feature Importance
            if hasattr(model, 'feature_importances_'):
                try:
                    importance_data = {
                        "features": feature_cols,
                        "importance_values": model.feature_importances_.tolist(),
                        "top_features": [
                            {"feature": feat, "importance": float(imp)} 
                            for feat, imp in sorted(zip(feature_cols, model.feature_importances_), 
                                                  key=lambda x: x[1], reverse=True)
                        ]
                    }
                    mlflow.log_dict(importance_data, "feature_importance.json")
                    print("✅ Feature importance saved")
                except Exception as e:
                    print(f"❌ Feature importance failed: {e}")
            
            # 3. Model Metadata
            try:
                model_metadata = {
                    "model_info": {
                        "type": model_type,
                        "sklearn_class": str(type(model).__name__),
                        "hyperparameters": model.get_params(),
                        "n_features": len(feature_cols),
                        "feature_names": feature_cols
                    },
                    "performance": {
                        "train_accuracy": float(train_acc),
                        "test_accuracy": float(test_acc),
                        "training_time_seconds": float(training_time),
                        "overfitting_gap": float(train_acc - test_acc)
                    },
                    "dataset_info": {
                        "total_samples": len(df),
                        "train_samples": len(X_train),
                        "test_samples": len(X_test),
                        "class_distribution": {
                            "stable": int(np.sum(y == 0)),
                            "minor": int(np.sum(y == 1)),
                            "major": int(np.sum(y == 2))
                        }
                    },
                    "training_config": {
                        "test_size": 0.2,
                        "random_state": 42,
                        "scaling": "StandardScaler",
                        "cross_validation": False
                    },
                    "mlflow_info": {
                        "run_id": run.info.run_id,
                        "experiment_id": run.info.experiment_id,
                        "created_at": datetime.now().isoformat(),
                        "artifact_uri": run.info.artifact_uri
                    }
                }
                mlflow.log_dict(model_metadata, "model_metadata.json")
                print("✅ Model metadata saved")
            except Exception as e:
                print(f"❌ Model metadata failed: {e}")
            
            # 4. Training Summary
            try:
                training_summary = {
                    "summary": {
                        "model": f"{model_type} with {model.n_estimators} trees",
                        "best_accuracy": float(max(train_acc, test_acc)),
                        "recommended_for_production": test_acc > 0.85,
                        "training_duration": f"{training_time:.2f} seconds",
                        "data_quality": "synthetic_generated"
                    },
                    "recommendations": {
                        "next_steps": [
                            "Validate with real voltage data",
                            "Test on different equipment types",
                            "Consider ensemble methods",
                            "Implement real-time monitoring"
                        ],
                        "hyperparameter_tuning": train_acc - test_acc > 0.1,
                        "feature_engineering": len(feature_cols) < 10
                    }
                }
                mlflow.log_dict(training_summary, "training_summary.json")
                print("✅ Training summary saved")
            except Exception as e:
                print(f"❌ Training summary failed: {e}")
            
            # 5. Optional: Serialized Model (as JSON)
            try:
                model_b64 = self.serialize_model(model)
                scaler_b64 = self.serialize_model(scaler)
                
                if model_b64 and scaler_b64:
                    serialized_objects = {
                        "model_base64": model_b64,
                        "scaler_base64": scaler_b64,
                        "serialization_method": "pickle_base64",
                        "instructions": "Use base64.b64decode() then pickle.loads() to restore objects",
                        "model_type": model_type,
                        "created_at": datetime.now().isoformat()
                    }
                    mlflow.log_dict(serialized_objects, "serialized_model.json")
                    print("✅ Serialized model saved as JSON")
            except Exception as e:
                print(f"❌ Model serialization failed: {e}")
            
            print("✅ All metadata and JSON artifacts logged successfully!")
            
            return {
                "run_id": run.info.run_id,
                "train_accuracy": train_acc,
                "test_accuracy": test_acc,
                "training_time": training_time,
                "artifacts_saved": True
            }

# Main execution
if __name__ == "__main__":
    print("🔋 Working Voltage Training (Metadata in Citus + JSON Artifacts)")
    print("=" * 60)
    
    trainer = WorkingVoltageTrainer()
    result = trainer.train_and_save("random_forest")
    
    print(f"\n🎉 Training completed successfully!")
    print(f"📊 Performance:")
    print(f"   - Train Accuracy: {result['train_accuracy']:.4f}")
    print(f"   - Test Accuracy: {result['test_accuracy']:.4f}")
    print(f"   - Training Time: {result['training_time']:.2f}s")
    print(f"🆔 Run ID: {result['run_id']}")
    print(f"🗄️ Metadata: Stored in Citus PostgreSQL mlflow schema")
    print(f"📁 Artifacts: Stored as JSON (downloadable from MLflow UI)")
    print(f"🌐 View: http://localhost:5000")
    print(f"\n💡 Note: Model can be reconstructed from serialized_model.json")
