#!/bin/bash

# Build Azure Kinect with Mesa software rendering - VPN compatible
echo "Building Azure Kinect with Mesa software rendering (Universal compatibility)..."

DOCKER_BUILDKIT=1 docker build --network=host -t azure-kinect-mesa-vpn -f Dockerfile.mesa .

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Azure Kinect SDK with Mesa ready."
    echo "Run with: ./deploy-mesa-vpn.sh"
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
