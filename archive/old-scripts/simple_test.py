#!/usr/bin/env python3
import sys
import os

print("Testing Azure Kinect DK...")
print(f"Python version: {sys.version}")

# Test basic imports
try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError as e:
    print(f"NumPy import failed: {e}")
    sys.exit(1)

# Test k4a tools
print("\nTesting k4a-tools...")
os.system("k4aviewer --help")

print("\nTesting device detection...")
os.system("ls -la /dev/bus/usb/001/053 /dev/bus/usb/001/054 /dev/bus/usb/002/026 /dev/bus/usb/002/029")

print("\nTest completed!")
