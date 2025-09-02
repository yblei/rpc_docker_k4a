#!/bin/bash
# Build VPN-safe Ubuntu 22.04 Azure Kinect container with source compilation

echo "🏗️  Building Ubuntu 22.04 Azure Kinect container with VPN support..."
echo "This will compile Azure Kinect SDK from source with NVIDIA GPU support."
echo ""

# Build with host networking to bypass VPN DNS issues
DOCKER_BUILDKIT=1 docker build \
    --network=host \
    --progress=plain \
    -t azure-kinect-ubuntu22-vpn \
    -f Dockerfile.ubuntu22 \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Ubuntu 22.04 source build successful!"
    echo ""
    echo "Testing container..."
    
    # Quick test to verify the container works
    docker run --rm \
        --privileged \
        -e DISPLAY=${DISPLAY} \
        -e NVIDIA_VISIBLE_DEVICES=all \
        -e NVIDIA_DRIVER_CAPABILITIES=all \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v /dev:/dev \
        azure-kinect-ubuntu22-vpn \
        bash -c "echo 'Container test: OK' && k4aviewer --help | head -3"
    
    if [ $? -eq 0 ]; then
        echo "✅ Container test passed!"
    else
        echo "⚠️  Container built but test failed"
    fi
    
    echo ""
    echo "📋 Available images:"
    docker images | grep -E "(azure-kinect|kinect)" | head -10
    
else
    echo ""
    echo "❌ Ubuntu 22.04 build failed!"
    echo "The Mesa version (azure-kinect-mesa-vpn) is still available as backup."
    exit 1
fi
