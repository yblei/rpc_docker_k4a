#!/bin/bash

# Deploy Azure Kinect with Mesa software rendering
echo "Deploying Azure Kinect with Mesa software rendering (Universal)..."

# Run the container with necessary privileges and device access
echo "Starting Azure Kinect Mesa container..."
docker run -it --rm \
    --privileged \
    --network=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /dev:/dev:rw \
    -v /etc/udev/rules.d:/etc/udev/rules.d:rw \
    -v $(pwd)/99-k4a.rules:/etc/udev/rules.d/99-k4a.rules:ro \
    -v $(pwd):/test:rw \
    --device-cgroup-rule='c 81:* rmw' \
    --device-cgroup-rule='c 189:* rmw' \
    azure-kinect-mesa-vpn \
    "$@"

echo "Container finished."
