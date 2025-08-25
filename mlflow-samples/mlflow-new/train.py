import mlflow
import random
import time

# Point to your MLflow tracking server
mlflow.set_tracking_uri("http://localhost:5006")

# Create or get experiment
mlflow.set_experiment("demo-experiment")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.01)
    mlflow.log_param("l1_ratio", 0.1)

    for step in range(5):
        mlflow.log_metric("rmse", random.random(), step=step)
        time.sleep(1)

    with open("output.txt", "w") as f:
        f.write("Hello MLflow with Citus!")
    mlflow.log_artifact("output.txt")

