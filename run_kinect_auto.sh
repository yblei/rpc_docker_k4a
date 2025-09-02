#!/bin/bash

# Auto-detect Azure Kinect DK devices and run Docker container
echo "Auto-detecting Azure Kinect DK devices..."

# Find all Azure Kinect USB devices
KINECT_DEVICES=$(lsusb | grep -i "045e:097[a-e]" | awk '{print "/dev/bus/usb/"substr($2,1,3)"/"substr($4,1,3)}')

if [ -z "$KINECT_DEVICES" ]; then
    echo "[FAIL] No Azure Kinect devices found. Please check if the device is connected."
    exit 1
fi

echo "[INFO] Found Azure Kinect devices:"
for device in $KINECT_DEVICES; do
    if [ -e "$device" ]; then
        echo "  [OK] $device"
    else
        echo "  [WARN] $device (not accessible)"
    fi
done

# Build device flags for docker run
DEVICE_FLAGS=""
for device in $KINECT_DEVICES; do
    if [ -e "$device" ]; then
        DEVICE_FLAGS="$DEVICE_FLAGS --device=$device"
    fi
done

echo "[INFO] Starting Docker container with detected devices..."

# Get current user ID and group ID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

docker run --rm -it \
  --user "${USER_ID}:${GROUP_ID}" \
  $DEVICE_FLAGS \
  -v "$(pwd)":/workspace -w /workspace \
  kinect-test "$@"
