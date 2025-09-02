#!/bin/bash

echo "=== USB Speed Diagnostic for Azure Kinect ==="

# Find Azure Kinect devices and check their connection speed
echo "Azure Kinect USB connections:"
for device in $(lsusb | grep "045e:097[a-e]" | awk '{print $2":"$4}' | tr -d ':'); do
    bus=$(echo $device | cut -d: -f1)
    dev=$(echo $device | cut -d: -f2)
    device_path="/dev/bus/usb/$bus/$dev"
    
    # Get device info
    device_info=$(lsusb -s $bus:$dev)
    echo "Device: $device_info"
    
    # Check USB speed by looking at the bus speed
    bus_speed=$(lsusb -t | grep -A 10 -B 10 "Bus $bus" | grep "Driver=" | head -1)
    echo "Bus info: $bus_speed"
    
    # Check if device is on USB 3.0 port
    if lsusb -t | grep -A 20 "Bus $bus" | grep -q "5000M\|10000M\|20000M"; then
        echo "✅ USB 3.0+ detected (sufficient for depth)"
    elif lsusb -t | grep -A 20 "Bus $bus" | grep -q "480M"; then
        echo "⚠️ USB 2.0 detected (may cause depth issues)"
    else
        echo "❓ Unknown USB speed"
    fi
    
    echo "---"
done

echo ""
echo "Full USB topology:"
lsusb -t | grep -E "(5000M|10000M|20000M|480M|12M)"

echo ""
echo "Recommendation:"
echo "- For depth capture: Use USB 3.0+ ports (5000M, 10000M, or 20000M)"
echo "- Avoid USB 2.0 ports (480M) for depth functionality"
