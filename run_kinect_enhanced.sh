#!/bin/bash

echo "=== Azure Kinect Depth Fix - Enhanced Capabilities Approach ==="
echo "This approach adds specific capabilities and USB access patterns for depth engine"

# Configure DisplayLink power management
displaylink_dev=$(lsusb | grep DisplayLink | head -1)
if [[ -n "$displaylink_dev" ]]; then
    echo "Found DisplayLink: $displaylink_dev"
    displaylink_busnum=$(echo "$displaylink_dev" | cut -d' ' -f2)
    
    # Disable autosuspend for DisplayLink device
    displaylink_path="/sys/bus/usb/devices/${displaylink_busnum}-*"
    for path in $displaylink_path; do
        if [[ -f "$path/power/autosuspend" ]]; then
            echo "Disabling autosuspend for DisplayLink device at $path"
            echo -1 | sudo tee "$path/power/autosuspend" > /dev/null 2>&1 || true
        fi
    done
fi

# Find Azure Kinect devices
kinect_devices=($(lsusb | grep "045e:097[a-e]" | awk '{print "/dev/bus/usb/"$2"/"$4}' | tr -d ':'))

if [[ ${#kinect_devices[@]} -eq 0 ]]; then
    echo "No Azure Kinect devices found!"
    exit 1
fi

echo "Found ${#kinect_devices[@]} Azure Kinect devices:"
for device in "${kinect_devices[@]}"; do
    echo "  $device"
done

# Set comprehensive permissions
echo "Setting enhanced permissions for Azure Kinect devices..."
for device in "${kinect_devices[@]}"; do
    echo "Setting permissions for $device"
    sudo chmod 666 "$device"
done

# Also set permissions for the entire USB bus directories
for device in "${kinect_devices[@]}"; do
    bus_dir=$(dirname "$device")
    echo "Setting permissions for USB bus directory: $bus_dir"
    sudo chmod -R 666 "$bus_dir" 2>/dev/null || true
done

echo "Starting Azure Kinect container with ENHANCED CAPABILITIES for depth engine..."
docker run -it --rm \
    --name kinect_depth_enhanced \
    --cap-drop ALL \
    --cap-add DAC_OVERRIDE \
    --cap-add SYS_RAWIO \
    --cap-add SYS_ADMIN \
    --cap-add MKNOD \
    --device-cgroup-rule='c 189:* rmw' \
    --security-opt apparmor:unconfined \
    $(for device in "${kinect_devices[@]}"; do echo "--device=$device"; done) \
    -v "$(pwd)":/workspace \
    -v /dev/bus/usb:/dev/bus/usb:rw \
    -w /workspace \
    kinect-test python3 test_depth.py

echo "Docker container finished. Checking DisplayLink status..."
lsusb | grep DisplayLink || echo "DisplayLink not found - this indicates a problem"
