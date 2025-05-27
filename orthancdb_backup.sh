#!/bin/bash

# Script to backup a Docker named volume
# WARNING: This script does NOT stop the container using the volume.
# Backing up a live database without stopping the application can lead to
# inconsistent backups. Use with caution.

# --- Configuration ---
VOLUME_NAME="milvue-congress-orthancdb"
HOST_BACKUP_DIR="/home/wilfried/wgs-repo/milvue-demo-congress/db-bak"
BACKUP_FILENAME="ECR2025_EN_${VOLUME_NAME}_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
# --- End Configuration ---

echo "Starting backup for Docker volume: ${VOLUME_NAME}"
echo "WARNING: The container using this volume will NOT be stopped."
echo "This may lead to an inconsistent backup, especially for databases."
echo "Proceed with caution."
echo "----------------------------------------------------------------"

# 1. Create the backup directory on the host if it doesn't exist
echo "Ensuring backup directory exists: ${HOST_BACKUP_DIR}"
mkdir -p "${HOST_BACKUP_DIR}"
if [ $? -ne 0 ]; then
    echo "Error: Could not create backup directory ${HOST_BACKUP_DIR}. Exiting."
    exit 1
fi

# 2. Run the Docker command to backup the volume
echo "Backing up volume ${VOLUME_NAME} to ${HOST_BACKUP_DIR}/${BACKUP_FILENAME}..."
docker run --rm \
  -v "${VOLUME_NAME}:/data_in_volume" \
  -v "${HOST_BACKUP_DIR}:/backup_target_on_host" \
  alpine \
  tar -czvf "/backup_target_on_host/${BACKUP_FILENAME}" -C /data_in_volume .

if [ $? -eq 0 ]; then
    echo "Backup successful: ${HOST_BACKUP_DIR}/${BACKUP_FILENAME}"
else
    echo "Error: Backup failed."
    exit 1
fi

echo "----------------------------------------------------------------"
echo "Backup script finished."
echo "Remember to verify your backups regularly."
