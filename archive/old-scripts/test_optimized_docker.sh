#!/bin/bash
# test_optimized_docker.sh - Quick test of our optimized Docker setup

set -e

echo "🚀 Testing Optimized Azure Kinect Docker Setup"
echo "=============================================="
echo
echo "This uses the NVIDIA OpenGL base image approach from UOsaka-Harada-Laboratory"
echo "but removes all ROS overhead for faster builds and smaller images."
echo

# Build the optimized image
echo "📦 Building optimized Docker image..."
docker build -f Dockerfile.optimized -t kinect-optimized .

echo
echo "🎯 Testing Azure Kinect in optimized container..."
echo "Expected: Proper OpenGL context + working depth engine"
echo

# Allow X11 forwarding
xhost +local:

# Run the test
docker run -it --rm \
  --runtime=nvidia \
  --privileged \
  --pid=host \
  --network=host \
  -v /dev:/dev \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "$(pwd)/test_depth.py:/workspace/test_depth.py" \
  -e DISPLAY="$DISPLAY" \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  kinect-optimized python3 test_depth.py

echo
echo "🔧 If successful, you can also run k4aviewer:"
echo "docker run -it --rm --runtime=nvidia --privileged -v /dev:/dev -v /tmp/.X11-unix:/tmp/.X11-unix:rw -e DISPLAY=\$DISPLAY kinect-optimized k4aviewer"
