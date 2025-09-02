#!/bin/bash

echo "=== Azure Kinect Depth Fix - Privileged Docker Approach ==="
echo "This approach uses privileged mode and additional capabilities to fix depth engine error 204"

# Find DisplayLink device and configure power management
displaylink_dev=$(lsusb | grep DisplayLink | head -1)
if [[ -n "$displaylink_dev" ]]; then
    echo "Found DisplayLink: $displaylink_dev"
    displaylink_busnum=$(echo "$displaylink_dev" | cut -d' ' -f2)
    displaylink_devnum=$(echo "$displaylink_dev" | cut -d' ' -f4 | tr -d ':')
    echo "DisplayLink is at Bus ${displaylink_busnum} Device ${displaylink_devnum}"
    
    # Disable autosuspend for DisplayLink device
    displaylink_path="/sys/bus/usb/devices/${displaylink_busnum}-*"
    for path in $displaylink_path; do
        if [[ -f "$path/power/autosuspend" ]]; then
            echo "Disabling autosuspend for DisplayLink device at $path"
            echo -1 | sudo tee "$path/power/autosuspend" > /dev/null 2>&1 || true
        fi
    done
fi

# Find and configure Azure Kinect devices
echo "Configuring Azure Kinect devices..."
kinect_devices=($(lsusb | grep "045e:097[a-e]" | awk '{print "/dev/bus/usb/"$2"/"$4}' | tr -d ':'))

if [[ ${#kinect_devices[@]} -eq 0 ]]; then
    echo "No Azure Kinect devices found!"
    exit 1
fi

echo "Found ${#kinect_devices[@]} Azure Kinect devices:"
for device in "${kinect_devices[@]}"; do
    echo "  $device"
done

# Set permissions
echo "Setting permissions for Azure Kinect devices..."
for device in "${kinect_devices[@]}"; do
    echo "Setting permissions for $device"
    sudo chmod 666 "$device"
done

echo "Starting Azure Kinect container with PRIVILEGED MODE for depth engine..."
docker run -it --rm \
    --name kinect_depth_fix \
    --privileged \
    --cap-add=ALL \
    --device-cgroup-rule='c 189:* rmw' \
    -v /dev:/dev \
    -v /sys:/sys \
    -v "$(pwd)":/workspace \
    -w /workspace \
    kinect-test python3 test_depth.py

echo "Docker container finished. Checking DisplayLink status..."
lsusb | grep DisplayLink || echo "DisplayLink not found - this indicates a problem"
