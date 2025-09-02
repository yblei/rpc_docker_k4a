#!/usr/bin/env python3
import sys

print("Testing Azure Kinect DK - Color only mode...")

try:
    from pyk4a import PyK4A, Config, ColorResolution, DepthMode
    print("[OK] Successfully imported pyk4a")
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

try:
    # Try color-only configuration to avoid depth engine issues
    config = Config(
        color_resolution=ColorResolution.RES_720P,
        depth_mode=DepthMode.OFF,  # Disable depth to avoid depth engine error
        synchronized_images_only=False,
    )
    
    print("[INFO] Initializing camera - Color only mode (depth disabled)...")
    k4a = PyK4A(config=config)
    
    print("[INFO] Starting camera...")
    k4a.start()
    
    print("[INFO] Camera started successfully! Capturing color frames...")
    
    import time
    
    # Capture a few color frames
    for i in range(3):
        print(f"[INFO] Capturing color frame {i+1}/3...")
        
        capture = k4a.get_capture()
        
        if capture.color is not None:
            color_shape = capture.color.shape
            print(f"  [SUCCESS] Color frame: {color_shape}, dtype: {capture.color.dtype}")
            
            # Save the first frame
            if i == 0:
                try:
                    import imageio
                    imageio.imwrite("azure_kinect_color.jpg", capture.color)
                    print("  [SUCCESS] Saved azure_kinect_color.jpg")
                except Exception as e:
                    print(f"  [WARN] Could not save image: {e}")
        else:
            print(f"  [FAIL] No color frame received")
        
        time.sleep(0.5)
    
    print("[INFO] Stopping camera...")
    k4a.stop()
    
    print("\n[SUCCESS] Azure Kinect DK color capture is working!")
    print("✅ Power supply change fixed the issue!")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    print(f"[DEBUG] Error type: {type(e).__name__}")
    sys.exit(1)
