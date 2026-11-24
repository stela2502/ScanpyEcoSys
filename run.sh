#!/bin/bash

# Variables
VERSION=1.3
IMAGE_NAME="ScanpyEcoSys_v${VERSION}.sif"
SCRIPT=$(readlink -f $0)
IMAGE_PATH=`dirname $SCRIPT`

# Check if the image exists
if [ ! -f "${IMAGE_PATH}/${IMAGE_NAME}" ]; then
    echo "Error: Image ${IMAGE_NAME} not found in ${IMAGE_PATH}."
    exit 1
fi

# Run the image
echo "Running ${IMAGE_NAME}..."
unset PYTHONPATH
unset PYTHONHOME
apptainer exec -B /data1:/mnt/data1 -B /data2:/mnt/data2 -B /home "${IMAGE_PATH}/${IMAGE_NAME}" jupyter lab --port 9734 --ip=0.0.0.0 --allow-root --no-browser

