import mlflow
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

# Set your MLflow tracking URI
mlflow.set_tracking_uri("http://localhost:5004")

def create_sample_data():
    """Create sample dataset"""
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    
    # Convert to DataFrame for better handling
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    return df

def train_model(model_type="random_forest", experiment_name="ML_Experiments"):
    """Train a model and log to MLflow (without model artifacts)"""
    
    # Create or get experiment
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"✅ Created experiment: {experiment_name}")
    except Exception:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
        print(f"✅ Using existing experiment: {experiment_name}")
    
    # Create data
    df = create_sample_data()
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Start MLflow run
    with mlflow.start_run(experiment_id=experiment_id, run_name=f"{model_type}_experiment"):
        
        # Choose model based on type
        if model_type == "random_forest":
            n_estimators = 100
            max_depth = 10
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
            # Log parameters
            mlflow.log_param("model_type", "RandomForest")
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            
        elif model_type == "logstic_regression":
            C = 1.0
            model = LogisticRegression(C=C, random_state=42, max_iter=1000)
            # Log parameters
            mlflow.log_param("model_type", "LogisticRegression")
            mlflow.log_param("C", C)
        
        # Log dataset info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("n_features", X.shape[1])
        
        # Train model
        print(f"🚀 Training {model_type}...")
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        
        print(f"📊 Results:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall: {recall:.4f}")
        print(f"   F1-Score: {f1:.4f}")
        
        # Log additional custom metrics based on model type
        if model_type == "random_forest":
            # Log feature importance as individual metrics
            feature_importance = model.feature_importances_
            for i, importance in enumerate(feature_importance):
                mlflow.log_metric(f"feature_{i}_importance", importance)
            
            # Log the top 3 most important features
            top_features = np.argsort(feature_importance)[-3:][::-1]
            for j, feature_idx in enumerate(top_features):
                mlflow.log_param(f"top_{j+1}_feature", f"feature_{feature_idx}")
                mlflow.log_param(f"top_{j+1}_feature_importance", f"{feature_importance[feature_idx]:.4f}")
        
        # Try to log simple artifacts (these usually work)
        try:
            # Create and log visualizations
            
            # 1. Feature importance (for RandomForest)
            if model_type == "random_forest":
                plt.figure(figsize=(10, 6))
                feature_importance = model.feature_importances_
                feature_names = X.columns
                
                # Create feature importance plot
                indices = np.argsort(feature_importance)[::-1]
                plt.bar(range(len(feature_importance)), feature_importance[indices])
                plt.title("Feature Importance")
                plt.xlabel("Features")
                plt.ylabel("Importance")
                plt.xticks(range(len(feature_importance)), 
                          [feature_names[i] for i in indices], rotation=45)
                plt.tight_layout()
                plt.savefig("feature_importance.png", dpi=300, bbox_inches='tight')
                mlflow.log_artifact("feature_importance.png")
                plt.close()
            
            # 2. Confusion Matrix
            from sklearn.metrics import confusion_matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title("Confusion Matrix")
            plt.ylabel("True Label")
            plt.xlabel("Predicted Label")
            plt.savefig("confusion_matrix.png", dpi=300, bbox_inches='tight')
            mlflow.log_artifact("confusion_matrix.png")
            plt.close()
            
            # 3. Log sample data
            sample_data = X_test.head(10).copy()
            sample_data['true_label'] = y_test[:10].values
            sample_data['predicted_label'] = y_pred[:10]
            sample_data['prediction_probability'] = y_pred_proba[:10]
            sample_data.to_csv("sample_predictions.csv", index=False)
            mlflow.log_artifact("sample_predictions.csv")
            
            # 4. Log model summary
            with open("model_summary.txt", "w") as f:
                f.write(f"Model Training Summary\n")
                f.write(f"=====================\n")
                f.write(f"Model Type: {model_type}\n")
                f.write(f"Training Samples: {len(X_train)}\n")
                f.write(f"Test Samples: {len(X_test)}\n")
                f.write(f"Features: {X.shape[1]}\n")
                f.write(f"\nPerformance Metrics:\n")
                f.write(f"Accuracy: {accuracy:.4f}\n")
                f.write(f"Precision: {precision:.4f}\n")
                f.write(f"Recall: {recall:.4f}\n")
                f.write(f"F1-Score: {f1:.4f}\n")
                
                if model_type == "random_forest":
                    f.write(f"\nModel Parameters:\n")
                    f.write(f"n_estimators: {model.n_estimators}\n")
                    f.write(f"max_depth: {model.max_depth}\n")
            
            mlflow.log_artifact("model_summary.txt")
            print("✅ Artifacts logged successfully!")
            
        except Exception as e:
            print(f"⚠️  Could not log artifacts: {e}")
            print("But parameters and metrics are still logged!")
        
        # DON'T log the model object to avoid permission issues
        # Instead, log model metadata as parameters
        mlflow.log_param("model_saved", "locally_only")
        mlflow.log_param("model_class", str(type(model).__name__))
        
        print(f"✅ Experiment logged successfully!")
        print(f"🔗 Run ID: {mlflow.active_run().info.run_id}")
        print(f"📱 Check MLflow UI at: http://localhost:5004")
        
        # Clean up local files
        import os
        for file in ["feature_importance.png", "confusion_matrix.png", "sample_predictions.csv", "model_summary.txt"]:
            if os.path.exists(file):
                os.remove(file)
        
        return model, accuracy

def run_multiple_experiments():
    """Run multiple experiments to compare models"""
    print("🧪 Running multiple experiments...")
    
    models_to_test = ["random_forest", "logistic_regression"]
    results = {}
    
    for model_type in models_to_test:
        print(f"\n{'='*50}")
        print(f"Training {model_type}...")
        model, accuracy = train_model(model_type)
        results[model_type] = accuracy
    
    print(f"\n{'='*50}")
    print("📈 Final Results:")
    for model_name, acc in results.items():
        print(f"   {model_name}: {acc:.4f}")
    
    best_model = max(results, key=results.get)
    print(f"🏆 Best Model: {best_model} (Accuracy: {results[best_model]:.4f})")

if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import seaborn
    except ImportError:
        print("Installing seaborn...")
        import subprocess
        subprocess.check_call(["pip", "install", "seaborn"])
        import seaborn as sns
    
    print("🚀 Starting MLflow Training Example (No Model Artifacts)")
    print("="*60)
    
    # Option 1: Train single model
    print("Option 1: Single model training")
    train_model("random_forest")
    
    print("\n" + "="*60)
    
    # Option 2: Compare multiple models
    print("Option 2: Multiple model comparison")
    run_multiple_experiments()
    
    print(f"\n🎉 All experiments completed!")
    print(f"📱 Check your results at: http://localhost:5004")
    print(f"You should see:")
    print(f"  ✅ Experiments with runs")
    print(f"  ✅ Parameters and metrics")
    print(f"  ✅ Feature importance as metrics")
    print(f"  ✅ Visualizations (if artifact storage works)")
    print(f"  📝 Note: Models not stored as artifacts due to permission issues")
    print(f"       but all training metrics and parameters are tracked!")