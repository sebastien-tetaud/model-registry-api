#!/bin/bash

# Set the image name
IMAGE_NAME="model-registry-api"

echo "Running Docker container..."
docker run -d -p 8000:8000 --name $IMAGE_NAME $IMAGE_NAME

# Check if the container started successfully
if [ $? -eq 0 ]; then
    echo "Docker container started successfully."
    echo "You can access the app at http://localhost:8000"
else
    echo "Failed to start the Docker container." >&2
    exit 1
fi
