#!/usr/bin/env python3

import sys
import time

def test_depth_capture():
    """Test Azure Kinect depth frame capture"""
    
    print("Testing Azure Kinect DK - Depth capture...")
    
    try:
        import pyk4a
        from pyk4a import Config, PyK4A
        print("[OK] Successfully imported pyk4a")
    except ImportError as e:
        print(f"[FAIL] Could not import pyk4a: {e}")
        return False
    
    try:
        print("[INFO] Initializing camera with depth enabled...")
        
        # Configure for depth capture
        config = Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,  # Near field of view
            camera_fps=pyk4a.FPS.FPS_30,
            synchronized_images_only=True,
        )
        
        # Initialize camera
        k4a = PyK4A(config=config)
        print("[INFO] Starting camera...")
        k4a.start()
        
        print("[INFO] Camera started successfully! Capturing depth frames...")
        
        # Capture a few frames
        for i in range(3):
            print(f"[INFO] Capturing depth frame {i+1}/3...")
            
            try:
                capture = k4a.get_capture()
                
                if capture.depth is not None:
                    depth_frame = capture.depth
                    print(f"  [SUCCESS] Depth frame: {depth_frame.shape}, dtype: {depth_frame.dtype}")
                    print(f"  [INFO] Depth range: min={depth_frame.min()}mm, max={depth_frame.max()}mm")
                    
                    # Count valid depth pixels
                    valid_pixels = (depth_frame > 0).sum()
                    total_pixels = depth_frame.size
                    print(f"  [INFO] Valid depth pixels: {valid_pixels}/{total_pixels} ({100*valid_pixels/total_pixels:.1f}%)")
                else:
                    print(f"  [WARN] No depth frame captured")
                
                if capture.color is not None:
                    color_frame = capture.color
                    print(f"  [SUCCESS] Color frame: {color_frame.shape}, dtype: {color_frame.dtype}")
                else:
                    print(f"  [WARN] No color frame captured")
                    
            except Exception as e:
                print(f"  [ERROR] Failed to capture frame: {e}")
                print(f"  [DEBUG] Error type: {type(e).__name__}")
            
            time.sleep(0.5)
        
        print("[INFO] Stopping camera...")
        k4a.stop()
        
        print("\n[SUCCESS] Azure Kinect DK depth capture test completed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Camera initialization failed: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_depth_capture()
    sys.exit(0 if success else 1)
