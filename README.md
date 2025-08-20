<img width="565" height="175" alt="image" src="https://github.com/user-attachments/assets/8b902fbe-92f5-4c65-ae60-a1bd359f3144" />




1. MLflow Server: Running in Docker using ghcr.io/mlflow/mlflow pre-built image
2. Volume Mount: Persistent storage with mlflow-data/ folder
3. Training Pipeline: Python scripts that connect to dockerized MLflow

# used an official pre-built image
ghcr.io/mlflow/mlflow



#  Python training script runs locally
python3 train_model.py --mlflow-server http://localhost:5005
# ↑ Runs on host    ↑ Connects to Docker container


docker run -d \
  --name mlflow-volume \
  --user $(id -u):$(id -g) \
  -p 5005:5000 \
  -v $(pwd)/mlflow-data:/mlflow \
  ghcr.io/mlflow/mlflow \
  mlflow server \
  --backend-store-uri file:///mlflow/mlruns \
  --default-artifact-root file:///mlflow/mlartifacts \
  --host 0.0.0.0 \
  --port 5000

  docker logs mlflow-volume

  python3 train_voltage_model.py --mlflow-server http://localhost:5005




  <img width="1887" height="717" alt="image" src="https://github.com/user-attachments/assets/5b65f4d1-2961-4b82-a21f-140d544583fe" />
