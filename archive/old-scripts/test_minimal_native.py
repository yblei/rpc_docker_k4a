#!/usr/bin/env python3
"""
Test Azure Kinect with very conservative settings to avoid USB bandwidth issues
"""

import sys
import os

# Add the Docker container's Python path to test if modules work
sys.path.insert(0, '/usr/local/lib/python3.8/dist-packages')

try:
    import pyk4a
    from pyk4a import Config, PyK4A, ColorResolution, DepthMode, FPS
    
    print("=== Testing Azure Kinect with minimal settings ===")
    print("[OK] Successfully imported pyk4a")
    
    # Test with absolute minimal settings
    config = Config(
        color_resolution=ColorResolution.RES_720P,  # Lowest reasonable resolution
        depth_mode=DepthMode.OFF,  # No depth to minimize bandwidth
        camera_fps=FPS.FPS_5,  # Very low framerate to minimize bandwidth
        synchronized_images_only=False
    )
    
    print(f"[INFO] Config: {config.__dict__}")
    print("[INFO] Creating PyK4A object...")
    
    k4a = PyK4A(config=config)
    print("[INFO] PyK4A object created successfully")
    
    print("[INFO] Starting camera with minimal bandwidth config...")
    k4a.start()
    print("[SUCCESS] Camera started!")
    
    # Try to capture just one frame to test basic functionality
    print("[INFO] Attempting to capture one frame...")
    capture = k4a.get_capture()
    
    if capture.color is not None:
        print(f"[SUCCESS] Color frame captured! Shape: {capture.color.shape}")
        print("[SUCCESS] Basic Azure Kinect functionality is working!")
    else:
        print("[WARNING] No color data in capture")
    
    k4a.stop()
    print("[INFO] Camera stopped successfully")
    print("[SUCCESS] Test completed without errors!")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
