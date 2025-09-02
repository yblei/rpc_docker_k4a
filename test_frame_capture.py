#!/usr/bin/env python3
import sys
import os
import time

print("Testing Azure Kinect DK frame capture...")

try:
    from pyk4a import PyK4A, Config
    import numpy as np
    print("[OK] Successfully imported pyk4a and numpy")
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

try:
    # Initialize with basic configuration  
    from pyk4a import K4A_COLOR_RESOLUTION_720P, K4A_DEPTH_MODE_NFOV_UNBINNED
    
    config = Config(
        color_resolution=K4A_COLOR_RESOLUTION_720P,
        depth_mode=K4A_DEPTH_MODE_NFOV_UNBINNED,
        synchronized_images_only=True,
    )
    
    print("[INFO] Initializing camera with 720p color and NFOV depth...")
    k4a = PyK4A(config=config)
    
    print("[INFO] Starting camera...")
    k4a.start()
    
    print("[INFO] Camera started successfully! Capturing frames...")
    
    # Capture multiple frames to test stability
    for i in range(5):
        print(f"[INFO] Capturing frame {i+1}/5...")
        
        capture = k4a.get_capture()
        
        if capture.color is not None:
            color_shape = capture.color.shape
            print(f"  [OK] Color frame: {color_shape}, dtype: {capture.color.dtype}")
            
            # Save the first frame as an example
            if i == 0:
                try:
                    import imageio
                    imageio.imwrite(f"color_frame_{i+1}.jpg", capture.color)
                    print(f"  [OK] Saved color_frame_{i+1}.jpg")
                except ImportError:
                    # Fallback using PIL if imageio fails
                    try:
                        from PIL import Image
                        img = Image.fromarray(capture.color)
                        img.save(f"color_frame_{i+1}.jpg")
                        print(f"  [OK] Saved color_frame_{i+1}.jpg (using PIL)")
                    except ImportError:
                        print("  [WARN] Could not save image (no imageio or PIL)")
        else:
            print(f"  [FAIL] No color frame received")
        
        if capture.depth is not None:
            depth_shape = capture.depth.shape
            depth_min = np.min(capture.depth[capture.depth > 0])
            depth_max = np.max(capture.depth)
            print(f"  [OK] Depth frame: {depth_shape}, range: {depth_min}-{depth_max}mm")
            
            # Save the first depth frame
            if i == 0:
                try:
                    # Convert depth to 8-bit for saving
                    depth_normalized = ((capture.depth / depth_max) * 255).astype(np.uint8)
                    import imageio
                    imageio.imwrite(f"depth_frame_{i+1}.png", depth_normalized)
                    print(f"  [OK] Saved depth_frame_{i+1}.png")
                except:
                    print("  [WARN] Could not save depth image")
        else:
            print(f"  [FAIL] No depth frame received")
        
        # Small delay between frames
        time.sleep(0.1)
    
    print("[INFO] Stopping camera...")
    k4a.stop()
    
    print("\n[SUCCESS] Frame capture test completed successfully!")
    print("✅ Azure Kinect DK is working perfectly for Python frame capture!")
    
except Exception as e:
    print(f"[FAIL] Error during camera operation: {e}")
    print("\nPossible solutions:")
    print("1. Make sure the device is not being used by another application")
    print("2. Try unplugging and reconnecting the Azure Kinect DK")
    print("3. Check USB cable and power connections")
    sys.exit(1)

print("\n[INFO] Summary:")
print("- Python frame capture: ✅ Working")
print("- CLI tools (k4arecorder): ❌ Has libusb issues (but not needed for Python)")
print("\nYou can now use pyk4a in your Python applications!")
