#!/bin/bash

echo "=== DisplayLink Diagnostic ==="
echo "Date: $(date)"
echo ""

echo "1. DisplayLink USB devices:"
lsusb | grep -i displaylink || echo "   No DisplayLink devices found via lsusb"
echo ""

echo "2. DisplayLink service status:"
systemctl status displaylink-driver 2>/dev/null || echo "   DisplayLink service not found"
echo ""

echo "3. USB power management:"
echo "   USB autosuspend settings:"
for usb_device in /sys/bus/usb/devices/*/power/autosuspend_delay_ms; do
    if [ -r "$usb_device" ]; then
        device_path=$(dirname $(dirname "$usb_device"))
        device_name=$(basename "$device_path")
        autosuspend=$(cat "$usb_device" 2>/dev/null || echo "N/A")
        
        # Check if it's a DisplayLink or Azure Kinect device
        if [ -f "$device_path/idVendor" ] && [ -f "$device_path/idProduct" ]; then
            vendor=$(cat "$device_path/idVendor")
            product=$(cat "$device_path/idProduct")
            
            if [ "$vendor" = "17e9" ]; then
                echo "   $device_name (DisplayLink): autosuspend=${autosuspend}ms"
            elif [ "$vendor" = "045e" ] && [[ "$product" =~ ^097[a-e]$ ]]; then
                echo "   $device_name (Azure Kinect): autosuspend=${autosuspend}ms"
            fi
        fi
    fi
done
echo ""

echo "4. Current USB topology:"
lsusb -t
echo ""

echo "5. Kernel messages (last 20 USB-related):"
dmesg | grep -i "usb\|displaylink" | tail -20 || echo "   No recent USB messages"
echo ""

echo "=== Recommendations ==="
echo "If DisplayLink keeps disconnecting:"
echo "1. Try connecting Azure Kinect to a different USB port/hub"
echo "2. Use a powered USB hub for one of the devices"
echo "3. Disable USB autosuspend for DisplayLink devices"
echo "4. Install Azure Kinect SDK natively (no Docker)"
