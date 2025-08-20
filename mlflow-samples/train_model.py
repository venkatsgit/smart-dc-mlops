import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("🚀 Using existing MLflow server...")

# Use your existing working MLflow server
mlflow.set_tracking_uri("http://localhost:5005")
mlflow.set_experiment("simple-training")

print("📊 Generating training data...")
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🤖 Training model...")
with mlflow.start_run():
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Log only parameters and metrics (no model artifacts for now)
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("n_samples", len(X_train))
    
    print(f"✅ Model trained successfully!")
    print(f"�� Accuracy: {accuracy:.4f}")
    print(f"🌐 View results at: http://localhost:5005")
