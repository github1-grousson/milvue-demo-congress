#!/bin/bash

# Script to restore a Docker named volume from a .tar.gz backup
#
# !!! CRITICAL WARNING !!!
# This script does NOT stop or start any containers.
# You MUST MANUALLY STOP the container(s) using the target volume
# BEFORE running this script.
# You MUST MANUALLY START the container(s) AFTER a successful restore.
# Failure to do so can lead to data corruption or application failure.
# !!! CRITICAL WARNING !!!

# --- Configuration ---
VOLUME_NAME="milvue-congress-orthancdb"
# --- End Configuration ---

# Check if a backup file path is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/your/backup_file.tar.gz"
    echo "Example: $0 /home/wilfried/wgs-repo/milvue-demo-congress/db-bak/milvue-congress-orthancdb_backup_20250527_135100.tar.gz"
    exit 1
fi

BACKUP_FILE_PATH="$1"
BACKUP_FILENAME=$(basename "${BACKUP_FILE_PATH}")
HOST_BACKUP_DIR=$(dirname "${BACKUP_FILE_PATH}")

# Check if the backup file exists
if [ ! -f "${BACKUP_FILE_PATH}" ]; then
    echo "Error: Backup file not found at ${BACKUP_FILE_PATH}"
    exit 1
fi

echo "----------------------------------------------------------------"
echo "!!! CRITICAL WARNING !!!"
echo "This script will restore data to the Docker volume:"
echo "  Volume Name: ${VOLUME_NAME}"
echo "  From Backup File: ${BACKUP_FILE_PATH}"
echo ""
echo "This will OVERWRITE any existing data in the volume '${VOLUME_NAME}'."
echo "YOU MUST MANUALLY STOP ANY CONTAINER USING THIS VOLUME BEFORE PROCEEDING."
echo "----------------------------------------------------------------"
read -p "Have you manually stopped all containers using '${VOLUME_NAME}' and are you sure you want to proceed? (yes/NO): " CONFIRMATION

if [[ "${CONFIRMATION}" != "yes" ]]; then
    echo "Restore operation cancelled by user."
    exit 0
fi

echo "Starting restore for Docker volume: ${VOLUME_NAME}"
echo "Ensuring you have manually stopped containers using this volume..."

# Run the Docker command to restore the volume
# This will create the volume if it doesn't exist.
# It will clear the volume before extracting for a clean restore.
echo "Restoring volume ${VOLUME_NAME} from ${BACKUP_FILENAME}..."
docker run --rm \
  -v "${VOLUME_NAME}:/data_in_volume" \
  -v "${HOST_BACKUP_DIR}:/backup_source_on_host" \
  alpine \
  sh -c "echo 'Clearing existing data from /data_in_volume... (this may take a moment for large volumes)' && rm -rf /data_in_volume/* /data_in_volume/..?* /data_in_volume/.[!.]* && echo 'Extracting backup...' && tar -xzvf \"/backup_source_on_host/${BACKUP_FILENAME}\" -C /data_in_volume"

if [ $? -eq 0 ]; then
    echo "Restore successful: Volume ${VOLUME_NAME} restored from ${BACKUP_FILENAME}"
    echo ""
    echo "!!! IMPORTANT: You now need to MANUALLY START your Orthanc container (or any other container that uses this volume). !!!"
else
    echo "Error: Restore failed."
    echo "Please check the output above for details."
    echo "If the volume was partially written, it might be in an inconsistent state."
    exit 1
fi

echo "Restore script finished."
