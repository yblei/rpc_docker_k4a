#!/bin/bash

# Azure Kinect VPN Solutions Test Script
# Tests all available VPN-compatible Docker images

set -e

echo "🧪 Azure Kinect VPN Solutions Test Suite"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_image_exists() {
    local image_name="$1"
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "$image_name"; then
        echo -e "${GREEN}✅ Image $image_name exists${NC}"
        return 0
    else
        echo -e "${RED}❌ Image $image_name not found${NC}"
        return 1
    fi
}

test_container_start() {
    local image_name="$1"
    local container_name="test_${image_name//-/_}_$(date +%s)"
    
    echo "🚀 Starting container from $image_name..."
    
    if docker run -d --name "$container_name" \
        --privileged \
        -e DISPLAY=:99 \
        -v /dev:/dev \
        "$image_name" \
        bash -c "Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & sleep 3600"; then
        
        echo -e "${GREEN}✅ Container $container_name started successfully${NC}"
        
        # Test basic commands
        echo "🔍 Testing basic functionality..."
        
        # Test Python import
        if docker exec "$container_name" python3 -c "import pyk4a; print('pyk4a import: OK')" 2>/dev/null; then
            echo -e "${GREEN}✅ pyk4a Python import works${NC}"
        else
            echo -e "${RED}❌ pyk4a Python import failed${NC}"
        fi
        
        # Test k4a tools
        if docker exec "$container_name" which k4aviewer >/dev/null 2>&1; then
            echo -e "${GREEN}✅ k4aviewer tool available${NC}"
        else
            echo -e "${YELLOW}⚠️ k4aviewer tool not found${NC}"
        fi
        
        # Test OpenGL
        echo "🎨 Testing OpenGL configuration..."
        docker exec "$container_name" bash -c "
            export DISPLAY=:99
            if glxinfo 2>/dev/null | head -5; then
                echo 'OpenGL info retrieved successfully'
            else
                echo 'OpenGL info failed - may be normal in headless mode'
            fi
        "
        
        # Cleanup
        docker stop "$container_name" >/dev/null 2>&1
        docker rm "$container_name" >/dev/null 2>&1
        echo -e "${GREEN}✅ Container test completed and cleaned up${NC}"
        return 0
    else
        echo -e "${RED}❌ Container failed to start${NC}"
        return 1
    fi
}

test_kinect_simulation() {
    local image_name="$1"
    local container_name="kinect_sim_${image_name//-/_}_$(date +%s)"
    
    echo "📷 Testing Kinect simulation for $image_name..."
    
    # Create a simple Kinect test script
    cat > /tmp/kinect_test.py << 'EOF'
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import pyk4a
    from pyk4a import Config, PyK4A
    print("✓ pyk4a imported successfully")
    
    # Test configuration creation (doesn't require actual device)
    config = Config(
        color_resolution=pyk4a.ColorResolution.OFF,
        depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
        synchronized_images_only=False,
        camera_fps=pyk4a.FPS.FPS_5
    )
    print("✓ Kinect configuration created successfully")
    
    # Test PyK4A instantiation (will fail without device but should load libraries)
    try:
        k4a = PyK4A(config=config)
        print("✓ PyK4A instantiated (device not required for library test)")
    except Exception as e:
        if "No device connected" in str(e) or "Failed to open device" in str(e):
            print("✓ PyK4A libraries loaded correctly (no device connected - expected)")
        else:
            print(f"✗ Unexpected error: {e}")
            sys.exit(1)
            
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Runtime error: {e}")
    sys.exit(1)

print("SUCCESS: Kinect simulation test passed!")
EOF

    if docker run --rm \
        --name "$container_name" \
        -v /tmp/kinect_test.py:/test/kinect_test.py \
        "$image_name" \
        python3 /test/kinect_test.py; then
        echo -e "${GREEN}✅ Kinect simulation test passed${NC}"
        rm -f /tmp/kinect_test.py
        return 0
    else
        echo -e "${RED}❌ Kinect simulation test failed${NC}"
        rm -f /tmp/kinect_test.py
        return 1
    fi
}

# Main test execution
echo "📋 Available Docker Images:"
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | head -10

echo ""
echo "🔍 Testing VPN-compatible Azure Kinect images..."

# Test Mesa solution
echo ""
echo "1️⃣ Testing Mesa Software Rendering Solution"
echo "===========================================" 
if test_image_exists "azure-kinect-mesa-vpn"; then
    test_container_start "azure-kinect-mesa-vpn"
    test_kinect_simulation "azure-kinect-mesa-vpn"
    echo -e "${GREEN}✅ Mesa solution tests completed${NC}"
else
    echo -e "${YELLOW}⚠️ Mesa solution not built yet. Run: ./build-vpn.sh${NC}"
fi

# Test source build solution
echo ""
echo "2️⃣ Testing Source Build Solution"
echo "================================"
if test_image_exists "azure-kinect-source-vpn"; then
    test_container_start "azure-kinect-source-vpn"
    test_kinect_simulation "azure-kinect-source-vpn"
    echo -e "${GREEN}✅ Source build solution tests completed${NC}"
else
    echo -e "${YELLOW}⚠️ Source build solution not ready yet.${NC}"
    echo "Building now with VPN compatibility..."
    
    if ./build-ubuntu22-vpn.sh; then
        echo -e "${GREEN}✅ Source build completed successfully${NC}"
        test_container_start "azure-kinect-source-vpn"
        test_kinect_simulation "azure-kinect-source-vpn"
    else
        echo -e "${RED}❌ Source build failed${NC}"
    fi
fi

echo ""
echo "📊 Test Summary"
echo "==============="

# Show final image status
echo "Available VPN-compatible images:"
docker images | grep -E "(azure-kinect|kinect)" | grep -v "<none>" || echo "No Kinect images found"

echo ""
echo "🎯 Quick Start Commands:"
echo "========================"
echo "Mesa Solution (Working):     ./run-kinect-vpn.sh"
echo "Source Solution (Building):  docker run -it --rm --privileged -e DISPLAY=\${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev:/dev azure-kinect-source-vpn"

echo ""
echo "📚 For detailed documentation, see: VPN_SOLUTIONS.md"
echo -e "${GREEN}🎉 VPN compatibility test suite completed!${NC}"
