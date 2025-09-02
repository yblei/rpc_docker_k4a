#!/bin/bash

# Run Azure Kinect DK Docker container with targeted USB privileges (DisplayLink-safe)
echo "Starting Azure Kinect DK Docker container with targeted USB access..."

# Find Azure Kinect devices
KINECT_DEVICES=$(lsusb | grep -i "045e:097[a-e]" | awk '{print "/dev/bus/usb/"substr($2,1,3)"/"substr($4,1,3)}')

if [ -z "$KINECT_DEVICES" ]; then
    echo "[FAIL] No Azure Kinect devices found."
    exit 1
fi

echo "[INFO] Found Azure Kinect devices:"
for device in $KINECT_DEVICES; do
    echo "  - $device"
done

# Build device flags
DEVICE_FLAGS=""
for device in $KINECT_DEVICES; do
    DEVICE_FLAGS="$DEVICE_FLAGS --device=$device"
done

# Run with limited privileges - only map Kinect devices, not entire /dev
sudo docker run --rm -it --privileged \
  $DEVICE_FLAGS \
  -v "$(pwd)":/workspace -w /workspace \
  kinect-test "$@"

# Note: We still need --privileged for the Azure Kinect SDK to work,
# but we're not mapping the entire /dev directory
