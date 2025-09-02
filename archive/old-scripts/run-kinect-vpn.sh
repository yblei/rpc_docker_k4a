#!/bin/bash
# Azure Kinect VPN-friendly Docker launcher

echo "🚀 Starting Azure Kinect Mesa container (VPN-compatible)"
echo ""

# Allow X11 connections
xhost +local: >/dev/null 2>&1

# Run the VPN-compatible Mesa container
docker run -it --rm \
    --privileged \
    --dns=8.8.8.8 \
    --dns=8.8.4.4 \
    -e DISPLAY=${DISPLAY} \
    -e LIBGL_ALWAYS_SOFTWARE=1 \
    -e MESA_GL_VERSION_OVERRIDE=4.6 \
    -e MESA_GLSL_VERSION_OVERRIDE=460 \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /dev:/dev \
    -v $(pwd):/workspace \
    --name k4a_vpn \
    azure-kinect-mesa-vpn \
    bash

echo ""
echo "Container exited. Cleaning up X11 permissions..."
xhost -local: >/dev/null 2>&1
