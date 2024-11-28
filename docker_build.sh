#!/bin/bash

DOCKER_IMAGE_NAME=model-registry-api
DOCKERFILE=`pwd`
docker build -t $DOCKER_IMAGE_NAME -f $DOCKERFILE/Dockerfile .