#!/bin/bash

echo "Setting up USB power management to prevent DisplayLink conflicts..."

# Find DisplayLink device
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

# Set permissions for Azure Kinect devices only
echo "Setting permissions for Azure Kinect devices..."
for device in "${kinect_devices[@]}"; do
    echo "Setting permissions for $device"
    sudo chmod 666 "$device"
done

# Find video devices for Azure Kinect
echo "Configuring video devices for Azure Kinect..."
video_devices=($(ls /dev/video* 2>/dev/null))
echo "Found video devices: ${video_devices[@]}"

# Get user's video group GID
video_gid=$(getent group video | cut -d: -f3)
plugdev_gid=$(getent group plugdev | cut -d: -f3)
echo "Video group GID: $video_gid"
echo "Plugdev group GID: $plugdev_gid"

# Run Docker with network isolation and limited capabilities
echo "Starting Azure Kinect container with video device access..."
docker run -it --rm \
    --name kinect_test_pm_safe \
    --network none \
    --cap-drop ALL \
    --cap-add DAC_OVERRIDE \
    --security-opt no-new-privileges:true \
    --user $(id -u):$(id -g) \
    --group-add $video_gid \
    --group-add $plugdev_gid \
    $(for device in "${kinect_devices[@]}"; do echo "--device=$device"; done) \
    $(for device in "${video_devices[@]}"; do echo "--device=$device"; done) \
    -v "$(pwd)":/workspace \
    -w /workspace \
    kinect-test-usb-optimized python3 test_depth.py

echo "Docker container finished. DisplayLink should remain stable."
echo "Checking DisplayLink status..."
lsusb | grep DisplayLink || echo "DisplayLink not found - this indicates a problem"
