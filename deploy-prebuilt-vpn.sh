#!/bin/bash

# Deploy Azure Kinect with prebuilt Microsoft packages
echo "Deploying Azure Kinect with prebuilt Microsoft packages (NVIDIA OpenGL)..."

# Check if NVIDIA Docker runtime is available
if docker info | grep -q "nvidia"; then
    echo "✅ NVIDIA Docker runtime detected"
    RUNTIME_ARGS="--runtime=nvidia"
else
    echo "⚠️  NVIDIA Docker runtime not detected, using default runtime"
    RUNTIME_ARGS=""
fi

# Run the container with necessary privileges and device access
echo "Starting Azure Kinect container..."
docker run -it --rm \
    $RUNTIME_ARGS \
    --privileged \
    --network=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /dev:/dev:rw \
    -v /etc/udev/rules.d:/etc/udev/rules.d:rw \
    -v $(pwd)/99-k4a.rules:/etc/udev/rules.d/99-k4a.rules:ro \
    --device-cgroup-rule='c 81:* rmw' \
    --device-cgroup-rule='c 189:* rmw' \
    azure-kinect-prebuilt-vpn \
    "$@"

echo "Container finished."
