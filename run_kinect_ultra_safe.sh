#!/bin/bash

# Ultra-safe approach: Check USB topology and avoid DisplayLink conflicts
echo "Analyzing USB topology for safe Azure Kinect access..."

# Check which USB buses the devices are on
echo "DisplayLink devices:"
lsusb | grep -i displaylink || echo "  No DisplayLink devices found"

echo ""
echo "Azure Kinect devices:"
lsusb | grep -i "045e:097[a-e]"

echo ""
echo "Full USB topology:"
lsusb -t

echo ""
echo "Checking for USB hub conflicts..."

# Get DisplayLink bus info
DISPLAYLINK_BUS=$(lsusb | grep -i displaylink | awk '{print $2}' | head -1)
KINECT_BUSES=$(lsusb | grep -i "045e:097[a-e]" | awk '{print $2}' | sort -u)

if [ ! -z "$DISPLAYLINK_BUS" ]; then
    echo "DisplayLink is on USB bus: $DISPLAYLINK_BUS"
    echo "Azure Kinect is on USB buses: $KINECT_BUSES"
    
    # Check if they share the same bus
    for bus in $KINECT_BUSES; do
        if [ "$bus" = "$DISPLAYLINK_BUS" ]; then
            echo "⚠️  WARNING: DisplayLink and Azure Kinect share USB bus $bus"
            echo "   This may cause power/bandwidth conflicts"
        fi
    done
fi

echo ""
echo "Would you like to continue? (y/n)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    exit 0
fi

# Proceed with minimal Docker footprint
echo "Using minimal Docker configuration..."

KINECT_DEVICES=$(lsusb | grep -i "045e:097[a-e]" | awk '{print "/dev/bus/usb/"substr($2,1,3)"/"substr($4,1,3)}')

# Set permissions without systemd/udev interference
for device in $KINECT_DEVICES; do
    if [ -e "$device" ]; then
        echo "Setting permissions for $device"
        sudo chmod 666 "$device"
    fi
done

# Minimal Docker run - no volume mounts to /dev or /sys
DEVICE_FLAGS=""
for device in $KINECT_DEVICES; do
    DEVICE_FLAGS="$DEVICE_FLAGS --device=$device"
done

# Add network isolation and minimal capabilities
docker run --rm -it \
  --network none \
  --cap-drop ALL \
  --cap-add DAC_OVERRIDE \
  $DEVICE_FLAGS \
  -v "$(pwd)":/workspace -w /workspace \
  kinect-test "$@"

echo ""
echo "Docker container finished. Checking DisplayLink status..."
sleep 2
lsusb | grep -i displaylink || echo "DisplayLink not detected"
