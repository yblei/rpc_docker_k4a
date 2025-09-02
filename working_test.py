#!/usr/bin/env python3
import sys
import os

print("Testing Azure Kinect DK with k4aviewer...")

# First test: Use k4aviewer to see if device is detected
print("1. Checking device detection with k4aviewer:")
os.system("k4aviewer --list")

print("\n2. Testing basic device info:")
os.system("k4arecorder --help | head -10")

print("\n3. Testing device permissions:")
for device in ["/dev/bus/usb/001/053", "/dev/bus/usb/001/054", "/dev/bus/usb/002/026", "/dev/bus/usb/002/029"]:
    if os.path.exists(device):
        print(f"[OK] Device {device} is accessible")
    else:
        print(f"[FAIL] Device {device} not found")

# Try basic pyk4a import without advanced features
print("\n4. Testing pyk4a library:")
try:
    # Import basic k4a functionality
    from pyk4a import PyK4A
    print("[OK] pyk4a library imported successfully")
    
    # Try to initialize (might fail if no device or permissions issue)
    try:
        k4a = PyK4A()
        print("[OK] PyK4A initialized successfully")
        print("[OK] Azure Kinect DK is ready for use!")
    except Exception as e:
        print(f"[WARN] PyK4A initialization failed: {e}")
        print("This might be due to device permissions or the device not being connected.")
        
except ImportError as e:
    print(f"[FAIL] pyk4a import failed: {e}")

print("\n5. Suggested next steps:")
print("- If device detection works, you can use k4aviewer for a GUI interface")
print("- For Python programming, fix any pyk4a import issues")
print("- For recording, use k4arecorder from the command line")

print("\nTest completed!")
