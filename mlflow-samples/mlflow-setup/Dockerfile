FROM ghcr.io/mlflow/mlflow:latest

# Install PostgreSQL driver
RUN pip install psycopg2-binary

# Set default command
CMD ["mlflow", "server", "--help"]
