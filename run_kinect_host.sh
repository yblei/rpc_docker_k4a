#!/bin/bash
# run_kinect_host.sh - Optimized Azure Kinect execution on host system
# This script provides reliable Azure Kinect depth capture using our optimized host configuration

set -e

echo "🎯 Azure Kinect Host Execution Script"
echo "======================================"

# Check if Azure Kinect is connected
echo "🔍 Checking Azure Kinect device..."
if ! lsusb | grep -q "045e:097a"; then
    echo "❌ Azure Kinect device not detected"
    echo "   Please ensure the device is connected and powered on"
    exit 1
fi
echo "✅ Azure Kinect device detected"

# Check user permissions
echo "🔍 Checking user permissions..."
if ! groups | grep -q video; then
    echo "❌ User $USER is not in the video group"
    echo "   Run: sudo usermod -a -G video $USER"
    echo "   Then log out and log back in"
    exit 1
fi

if ! groups | grep -q plugdev; then
    echo "❌ User $USER is not in the plugdev group"  
    echo "   Run: sudo usermod -a -G plugdev $USER"
    echo "   Then log out and log back in"
    exit 1
fi
echo "✅ User permissions configured correctly"

# Check USB buffer optimization
echo "🔍 Checking USB buffer optimization..."
current_buffer=$(cat /sys/module/usbcore/parameters/usbfs_memory_mb 2>/dev/null || echo "unknown")
if [ "$current_buffer" = "1000" ]; then
    echo "✅ USB buffer optimized: ${current_buffer}MB"
else
    echo "⚠️  USB buffer not optimal: ${current_buffer}MB (should be 1000MB)"
    echo "   Current session will still work with existing optimization"
fi

# Check if DisplayLink is stable
echo "🔍 Checking DisplayLink status..."
if pgrep -f displaylink > /dev/null; then
    echo "✅ DisplayLink service running (optimized for stability)"
else
    echo "ℹ️  DisplayLink not running (this is fine)"
fi

# Verify test script exists
echo "🔍 Checking test script..."
if [ ! -f "test_depth.py" ]; then
    echo "❌ test_depth.py not found in current directory"
    echo "   Please ensure you're in the correct directory"
    exit 1
fi
echo "✅ Test script found"

# Set optimal environment
export KINECT_OPTIMIZED=true
echo "🔧 Environment configured for optimal performance"

echo ""
echo "🚀 Starting Azure Kinect depth capture..."
echo "   Expected output: 576x640 depth + 720x1280 color"
echo "   Press Ctrl+C to stop"
echo ""

# Run the test
python3 test_depth.py
