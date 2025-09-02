#!/bin/bash

# Azure Kinect VPN-Safe Deployment Script
# One-stop solution for all VPN-compatible Azure Kinect Docker needs

set -e

echo "🚀 Azure Kinect VPN-Safe Deployment"
echo "===================================="

# Configuration
MESA_IMAGE="azure-kinect-mesa-vpn"
SOURCE_IMAGE="azure-kinect-source-vpn"
PREFERRED_IMAGE="azure-kinect-source-vpn"  # Use NVIDIA OpenGL by default

# Helper functions
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  quick-start    - Run the NVIDIA OpenGL solution (preferred)"
    echo "  mesa          - Run Mesa software rendering solution (fallback)"
    echo "  build-source   - Build NVIDIA OpenGL source solution (VPN-safe)"
    echo "  build-mesa     - Build Mesa software rendering solution (VPN-safe)"
    echo "  test          - Test all available solutions"
    echo "  status        - Show status of all images"
    echo "  clean         - Remove all Azure Kinect Docker images"
    echo ""
    echo "Options:"
    echo "  --with-device  - Run with actual Kinect device access"
    echo "  --debug       - Run in debug mode with verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 quick-start                    # Run NVIDIA OpenGL solution (best performance)"
    echo "  $0 mesa                           # Run Mesa fallback if needed"
    echo "  $0 quick-start --with-device      # Run with real Kinect"
    echo "  $0 build-source                   # Build VPN-safe NVIDIA solution"
    echo "  $0 test                           # Test all solutions"
}

check_image_exists() {
    local image_name="$1"
    docker images --format "{{.Repository}}" | grep -q "^${image_name}$"
}

run_preferred_solution() {
    local with_device="$1"
    
    # Try NVIDIA OpenGL source build first
    if check_image_exists "$SOURCE_IMAGE"; then
        echo "🏃 Running NVIDIA OpenGL source solution (high performance)..."
        run_solution "$SOURCE_IMAGE" "$with_device" "NVIDIA OpenGL (Hardware Accelerated)"
    elif check_image_exists "$MESA_IMAGE"; then
        echo "🏃 Running Mesa fallback solution (software rendering)..."
        echo "💡 For better performance, run: $0 build-source"
        run_solution "$MESA_IMAGE" "$with_device" "Mesa Software Rendering (Fallback)"
    else
        echo "❌ No images found. Building NVIDIA OpenGL solution..."
        build_source
        if check_image_exists "$SOURCE_IMAGE"; then
            run_solution "$SOURCE_IMAGE" "$with_device" "NVIDIA OpenGL (Hardware Accelerated)"
        else
            echo "❌ Build failed. Try: $0 build-mesa for fallback solution"
            exit 1
        fi
    fi
}

run_solution() {
    local image_name="$1"
    local with_device="$2"
    local description="$3"
    
    local docker_cmd="docker run -it --rm --privileged"
    
    # Add NVIDIA runtime for source image
    if [[ "$image_name" == "$SOURCE_IMAGE" ]]; then
        docker_cmd="$docker_cmd --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all"
    fi
    
    # Add device access if requested
    if [[ "$with_device" == "true" ]]; then
        docker_cmd="$docker_cmd -v /dev:/dev"
        echo "🔌 Device access enabled for real Kinect"
    fi
    
    # Add display forwarding
    docker_cmd="$docker_cmd -e DISPLAY=\${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix"
    
    # Run the container
    eval "$docker_cmd $image_name bash -c '
        echo \"🎯 Azure Kinect VPN-Safe Environment\"
        echo \"==========================================\"
        echo \"Solution: $description\"
        echo \"VPN Safe: Yes ✅\"
        echo \"\"
        echo \"Available commands:\"
        echo \"  k4aviewer     - Launch Kinect viewer\"
        echo \"  python3       - Python with pyk4a support\"
        echo \"\"
        echo \"Example Python test:\"
        echo \"  python3 -c \\\"import pyk4a; print(\\\\\\\"Azure Kinect SDK ready!\\\\\\\")\\\"\"
        echo \"\"
        exec bash
    '"
}

run_mesa_solution() {
    local with_device="$1"
    
    if ! check_image_exists "$MESA_IMAGE"; then
        echo "❌ Mesa image not found. Building it now..."
        build_mesa
    fi
    
    echo "🏃 Running Mesa VPN-safe solution..."
    run_solution "$MESA_IMAGE" "$with_device" "Mesa Software Rendering (5 FPS depth)"
}

build_mesa() {
    echo "🔨 Building Mesa VPN-safe solution..."
    if [[ -f "./build-vpn.sh" ]]; then
        ./build-vpn.sh
    else
        echo "❌ build-vpn.sh not found. Creating it..."
        cat > build-vpn.sh << 'EOF'
#!/bin/bash
set -e
echo "Building VPN-safe Mesa solution..."
DOCKER_BUILDKIT=1 docker build --network=host -t azure-kinect-mesa-vpn -f Dockerfile.mesa .
echo "✅ Mesa VPN-safe build completed!"
EOF
        chmod +x build-vpn.sh
        ./build-vpn.sh
    fi
}

build_source() {
    echo "🔨 Building high-performance source solution (this may take 30+ minutes)..."
    if [[ -f "./Dockerfile.k4a-source" ]]; then
        DOCKER_BUILDKIT=1 docker build --network=host -t "$SOURCE_IMAGE" -f Dockerfile.k4a-source .
    else
        echo "❌ Dockerfile.k4a-source not found. Please ensure all files are present."
        exit 1
    fi
}

test_solutions() {
    echo "🧪 Testing all VPN-compatible solutions..."
    if [[ -f "./test-vpn-solutions.sh" ]]; then
        ./test-vpn-solutions.sh
    else
        echo "❌ Test script not found. Running basic tests..."
        
        # Basic test
        if check_image_exists "$MESA_IMAGE"; then
            echo "✅ Mesa image exists"
            docker run --rm "$MESA_IMAGE" python3 -c "import pyk4a; print('Mesa solution working!')"
        else
            echo "❌ Mesa image not found"
        fi
        
        if check_image_exists "$SOURCE_IMAGE"; then
            echo "✅ Source image exists" 
            docker run --rm "$SOURCE_IMAGE" python3 -c "import pyk4a; print('Source solution working!')"
        else
            echo "❌ Source image not found"
        fi
    fi
}

show_status() {
    echo "📊 Azure Kinect Docker Images Status"
    echo "===================================="
    
    echo ""
    echo "🔍 Available Images:"
    docker images | grep -E "(azure-kinect|kinect)" | grep -v "<none>" || echo "No Kinect images found"
    
    echo ""
    echo "📋 Solution Status:"
    
    if check_image_exists "$SOURCE_IMAGE"; then
        local size=$(docker images --format "table {{.Repository}}\t{{.Size}}" | grep "$SOURCE_IMAGE" | awk '{print $2}')
        echo "✅ NVIDIA OpenGL Solution: Ready ($size) - VPN Safe, Hardware Acceleration, High Performance"
    else
        echo "❌ NVIDIA OpenGL Solution: Not built (run: $0 build-source)"
    fi
    
    if check_image_exists "$MESA_IMAGE"; then
        local size=$(docker images --format "table {{.Repository}}\t{{.Size}}" | grep "$MESA_IMAGE" | awk '{print $2}')
        echo "✅ Mesa Fallback: Ready ($size) - VPN Safe, Software Rendering"
    else
        echo "❌ Mesa Fallback: Not built (run: $0 build-mesa)"
    fi
    
    echo ""
    echo "🎯 Quick Commands:"
    echo "  Ready to use: $0 quick-start"
    echo "  With Kinect:  $0 quick-start --with-device"
}

clean_images() {
    echo "🧹 Cleaning up Azure Kinect Docker images..."
    
    # Remove specific images
    for image in "$MESA_IMAGE" "$SOURCE_IMAGE" "kinect-mesa" "kinect-optimized" "kinect-test" "kinect-test-fixed" "kinect-test-usb-optimized"; do
        if check_image_exists "$image"; then
            echo "Removing $image..."
            docker rmi "$image" || echo "Failed to remove $image"
        fi
    done
    
    # Remove any dangling images
    echo "Removing dangling images..."
    docker image prune -f
    
    echo "✅ Cleanup completed!"
}

# Main script logic
case "${1:-help}" in
    "quick-start")
        with_device="false"
        if [[ "$2" == "--with-device" ]]; then
            with_device="true"
        fi
        run_mesa_solution "$with_device"
        ;;
    "build-mesa")
        build_mesa
        ;;
    "build-source")
        build_source
        ;;
    "test")
        test_solutions
        ;;
    "status")
        show_status
        ;;
    "clean")
        clean_images
        ;;
    "help"|*)
        show_usage
        ;;
esac
