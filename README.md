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


<<<<<<< HEAD
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
=======


  <img width="1887" height="717" alt="image" src="https://github.com/user-attachments/assets/5b65f4d1-2961-4b82-a21f-140d544583fe" />


  <img width="1895" height="949" alt="image" src="https://github.com/user-attachments/assets/ec808855-d3b8-4b6a-ac15-09a820932406" />


  <img width="1575" height="888" alt="image" src="https://github.com/user-attachments/assets/d493b362-d960-46f9-b332-703929dc2101" />

  <img width="1611" height="886" alt="image" src="https://github.com/user-attachments/assets/c77a5b33-4dd9-4b4e-b03a-0848a32d9d23" />



  docker run -d \
>>>>>>> 586868b597fea0c68db7ccdce81227d259a9d0c6
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

<<<<<<< HEAD
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
=======
 Go to http://localhost:5005
 ✅ All your experiments are there!
 ✅ All your models are there!
 ✅ All your runs and metrics are there!



<img width="588" height="265" alt="image" src="https://github.com/user-attachments/assets/90a431b3-964b-4875-994e-b62030569e65" />



>>>>>>> 586868b597fea0c68db7ccdce81227d259a9d0c6
