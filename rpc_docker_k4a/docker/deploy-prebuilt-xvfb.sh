#!/bin/bash
# Deploy Azure Kinect Container mit integriertem Xvfb

echo "🐳 Starting Azure Kinect container with integrated virtual display..."

# Stop any existing container
docker stop azure-kinect-xvfb-container 2>/dev/null || true
docker rm azure-kinect-xvfb-container 2>/dev/null || true

# Run container with integrated Xvfb
docker run -it --rm \
    --name azure-kinect-xvfb-container \
    --runtime=nvidia \
    --privileged \
    --network=host \
    -v /dev:/dev:rw \
    -v /etc/udev/rules.d:/etc/udev/rules.d:rw \
    -v $(pwd):/workspace:rw \
    --device-cgroup-rule='c 81:* rmw' \
    --device-cgroup-rule='c 189:* rmw' \
    azure-kinect-prebuilt-vpn \
    "$@"

echo "Container stopped."
