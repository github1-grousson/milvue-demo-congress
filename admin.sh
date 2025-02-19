#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
docker run --name milvue-admin-tool --rm -it --network=host -v "$DIR/assets:/app/assets" -v "$DIR/templates:/app/templates" wilfriedmv/milvue-admin-tool:latest
