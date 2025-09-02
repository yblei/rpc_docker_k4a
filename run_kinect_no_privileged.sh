#!/bin/bash

# Alternative approach: Use USB groups instead of full privileged access
echo "Setting up USB permissions for Azure Kinect DK (DisplayLink-safe approach)..."

# Check if user is in plugdev group
if ! groups $USER | grep -q plugdev; then
    echo "Adding user to plugdev group (requires sudo)..."
    sudo usermod -a -G plugdev $USER
    echo "Please log out and log back in, then run this script again."
    exit 1
fi

# Set temporary permissions for current session
echo "Setting temporary USB permissions for Azure Kinect devices..."
KINECT_DEVICES=$(lsusb | grep -i "045e:097[a-e]" | awk '{print "/dev/bus/usb/"substr($2,1,3)"/"substr($4,1,3)}')

for device in $KINECT_DEVICES; do
    if [ -e "$device" ]; then
        echo "Setting permissions for $device"
        sudo chmod 666 "$device"
    fi
done

# Run without privileged mode
echo "Starting Docker container without privileged mode..."

DEVICE_FLAGS=""
for device in $KINECT_DEVICES; do
    DEVICE_FLAGS="$DEVICE_FLAGS --device=$device"
done

docker run --rm -it \
  $DEVICE_FLAGS \
  -v "$(pwd)":/workspace -w /workspace \
  kinect-test "$@"
