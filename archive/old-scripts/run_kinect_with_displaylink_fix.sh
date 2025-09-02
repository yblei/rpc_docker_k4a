#!/bin/bash

# Run Azure Kinect and restart DisplayLink afterward
echo "Running Azure Kinect DK with DisplayLink restart..."

# Store DisplayLink devices before running
echo "Detecting DisplayLink devices..."
DISPLAYLINK_DEVICES=$(lsusb | grep -i displaylink || echo "No DisplayLink devices found")
echo "DisplayLink devices: $DISPLAYLINK_DEVICES"

# Run the Kinect test
./run_kinect.sh "$@"

# Restart DisplayLink service after Docker
echo "Restarting DisplayLink service..."
if systemctl is-active --quiet displaylink-driver; then
    sudo systemctl restart displaylink-driver
    echo "DisplayLink service restarted"
elif command -v displaylink-installer >/dev/null 2>&1; then
    # Alternative restart method
    sudo service displaylink-driver restart
    echo "DisplayLink service restarted (alternative method)"
else
    echo "DisplayLink service not found. You may need to manually restart it."
    echo "Try: sudo systemctl restart displaylink-driver"
fi

echo "If DisplayLink still doesn't work, try unplugging and reconnecting the DisplayLink device."
