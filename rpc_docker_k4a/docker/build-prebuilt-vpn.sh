#!/bin/bash

# Build Azure Kinect with prebuilt Microsoft packages - VPN compatible
echo "Building Azure Kinect with prebuilt Microsoft packages (NVIDIA OpenGL)..."

DOCKER_BUILDKIT=1 docker build --network=host -t azure-kinect-prebuilt-vpn -f Dockerfile.k4a-prebuilt .

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Azure Kinect SDK with NVIDIA OpenGL ready."
    echo "Run with: ./deploy-prebuilt-vpn.sh"
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
