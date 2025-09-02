#!/usr/bin/env python3
"""
Test script for the new Azure Kinect camera with different configurations
"""

import pyk4a
from pyk4a import Config, PyK4A, ColorResolution, DepthMode, FPS
import numpy as np

def test_color_unsynchronized():
    """Test color capture without synchronized_images_only"""
    print("[TEST] Color only (unsynchronized)")
    config = Config(
        color_resolution=ColorResolution.RES_720P,
        depth_mode=DepthMode.OFF,
        camera_fps=FPS.FPS_30,
        synchronized_images_only=False  # Explicitly disable synchronization
    )
    
    try:
        print(f"[INFO] Config: {config.__dict__}")
        print("[INFO] Starting camera...")
        
        k4a = PyK4A(config=config)
        k4a.start()
        
        # Capture a few frames
        for i in range(5):
            capture = k4a.get_capture()
            if capture.color is not None:
                print(f"[SUCCESS] Frame {i+1}: Color shape: {capture.color.shape}")
            else:
                print(f"[WARNING] Frame {i+1}: No color data")
        
        k4a.stop()
        print("[SUCCESS] Color capture working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Color only failed: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return False

def test_depth_unsynchronized():
    """Test depth capture without synchronized_images_only"""
    print("\n[TEST] Depth only (unsynchronized)")
    config = Config(
        color_resolution=ColorResolution.OFF,
        depth_mode=DepthMode.NFOV_2X2BINNED,
        camera_fps=FPS.FPS_30,
        synchronized_images_only=False  # Explicitly disable synchronization
    )
    
    try:
        print(f"[INFO] Config: {config.__dict__}")
        print("[INFO] Starting camera...")
        
        k4a = PyK4A(config=config)
        k4a.start()
        
        # Capture a few frames
        for i in range(5):
            capture = k4a.get_capture()
            if capture.depth is not None:
                print(f"[SUCCESS] Frame {i+1}: Depth shape: {capture.depth.shape}")
            else:
                print(f"[WARNING] Frame {i+1}: No depth data")
        
        k4a.stop()
        print("[SUCCESS] Depth capture working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Depth only failed: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return False

def test_combined_unsynchronized():
    """Test color + depth without synchronized_images_only"""
    print("\n[TEST] Color + Depth (unsynchronized)")
    config = Config(
        color_resolution=ColorResolution.RES_720P,
        depth_mode=DepthMode.NFOV_2X2BINNED,
        camera_fps=FPS.FPS_30,
        synchronized_images_only=False  # Disable synchronization
    )
    
    try:
        print(f"[INFO] Config: {config.__dict__}")
        print("[INFO] Starting camera...")
        
        k4a = PyK4A(config=config)
        k4a.start()
        
        # Capture a few frames
        for i in range(5):
            capture = k4a.get_capture()
            color_ok = capture.color is not None
            depth_ok = capture.depth is not None
            print(f"[INFO] Frame {i+1}: Color: {color_ok}, Depth: {depth_ok}")
            
            if color_ok and depth_ok:
                print(f"[SUCCESS] Frame {i+1}: Color {capture.color.shape}, Depth {capture.depth.shape}")
        
        k4a.stop()
        print("[SUCCESS] Combined capture working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Combined capture failed: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("Testing new Azure Kinect DK - Unsynchronized modes...")
    print("[OK] Successfully imported pyk4a")
    
    # Test each mode
    results = {
        'color': test_color_unsynchronized(),
        'depth': test_depth_unsynchronized(), 
        'combined': test_combined_unsynchronized()
    }
    
    print(f"\n=== SUMMARY ===")
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test.upper()}: {status}")
