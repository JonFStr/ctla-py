#!/bin/sh
# Run the python script and sync with rclone afterwards
# Requires ctla_config.json and rclone.config to be present in /app and the rclone remote to be named sharepoint

echo "Song downloader started"

cd /app || exit 1

python -u /usr/src/tools/download_songs_sort_ext.py

echo "Download done, beginning upload"

rclone --config /app/rclone/config --streaming-upload-cutoff 4M --onedrive-upload-cutoff 4M copy "${OUTPUT_DIR}" "${REMOTE_NAME}:${REMOTE_PATH}"

echo "Upload done"
