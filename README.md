Host Machine               Docker Container
┌─────────────────┐       ┌──────────────────┐
│ train_model.py  │──────▶│ MLflow Server    │
│ (Python script)│ HTTP  │ (port 5005)      │
└─────────────────┘       └──────────────────┘



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


  Your Computer (Permanent)     Docker Container (Temporary)
┌─────────────────────┐      ┌────────────────────┐
│ mlflow-data/        │      │ /mlflow/           │
│   mlruns/           │◄────►│   mlruns/          │
│   mlartifacts/      │ SYNC │   mlartifacts/     │
│   experiments/      │      │   experiments/     │
│   models/           │      │   models/          │
└─────────────────────┘      └────────────────────┘
    ↑ PERSISTS                    ↑ GETS DELETED


   docker run -d \
  --name mlflow-volume \           # Container name
  --user $(id -u):$(id -g) \       # Run with YOUR user permissions (fixes volume issues)
  -p 5005:5000 \                   # Port mapping: localhost:5005 → container:5000
  -v $(pwd)/mlflow-data:/mlflow \   # Volume mount: local folder → container folder

  ghcr.io/mlflow/mlflow \             # Official MLflow image
mlflow server \                     # Start MLflow server
--backend-store-uri file:///mlflow/mlruns \        # Store experiments here
--default-artifact-root file:///mlflow/mlartifacts \ # Store models here
--host 0.0.0.0 \                    # Accept connections from anywhere
--port 5000                         # Server runs on port 5000 inside container


# Stop and remove the container
docker stop mlflow-volume
docker rm mlflow-volume

# Container is GONE, but data is safe
docker ps  # Container not listed
ls -la mlflow-data/  # Data still there!

# Run the SAME command
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

  # Check container is running
docker ps

# Go to http://localhost:5005
# ✅ All your experiments are there!
# ✅ All your models are there!
# ✅ All your runs and metrics are there!


What gets DELETED:        What stays PERMANENT:
┌─────────────────┐      ┌──────────────────────┐
│ ❌ Container     │      │ ✅ mlflow-data/      │
│ ❌ MLflow process│      │ ✅ All experiments   │
│ ❌ Memory state  │      │ ✅ All models        │
└─────────────────┘      │ ✅ All runs          │
                         │ ✅ All metrics       │
                         └──────────────────────┘