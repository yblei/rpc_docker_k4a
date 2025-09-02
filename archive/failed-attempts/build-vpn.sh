#!/bin/bash
# Docker build script with VPN support using host networking

echo "Building Azure Kinect containers with VPN-friendly network settings..."

echo "Building Mesa version (working solution) with host network..."
DOCKER_BUILDKIT=1 docker build \
    --network=host \
    -t azure-kinect-mesa-vpn \
    -f Dockerfile.mesa \
    . --progress=plain

if [ $? -eq 0 ]; then
    echo "✅ Mesa build successful!"
else
    echo "❌ Mesa build failed!"
    exit 1
fi

echo ""
echo "Building NVIDIA OpenGL source version with host network..."
DOCKER_BUILDKIT=1 docker build \
    --network=host \
    -t azure-kinect-source-vpn \
    -f Dockerfile.k4a-source \
    . --progress=plain

if [ $? -eq 0 ]; then
    echo "✅ NVIDIA OpenGL source build successful!"
else
    echo "⚠️  NVIDIA OpenGL source build failed, but Mesa version is available"
fi

echo ""
echo "Available images:"
docker images | grep -E "(azure-kinect|kinect)"
