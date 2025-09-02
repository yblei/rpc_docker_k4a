#!/bin/bash

# Run Azure Kinect DK Docker container without privileged mode
echo "Starting Azure Kinect DK Docker container..."

# Get current user ID and group ID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

docker run --rm -it \
  --user "${USER_ID}:${GROUP_ID}" \
  --device=/dev/bus/usb/001/053 \
  --device=/dev/bus/usb/001/054 \
  --device=/dev/bus/usb/002/026 \
  --device=/dev/bus/usb/002/029 \
  -v "$(pwd)":/workspace -w /workspace \
  kinect-test "$@"

# Usage examples:
# ./run_kinect_safe.sh                          # Interactive shell
# ./run_kinect_safe.sh python3 working_test.py  # Run test script
# ./run_kinect_safe.sh k4arecorder --list        # List devices
