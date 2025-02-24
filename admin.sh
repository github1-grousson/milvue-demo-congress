#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
docker run --name milvue-admin-tool --rm -it --network=host -e LOG_LEVEL=INFO -v /etc/localtime:/etc/localtime:ro -v "$DIR/assets:/app/assets" -v "$DIR/templates:/app/templates" -u $(id -u):$(id -g) wilfriedmv/milvue-admin-tool:latest
