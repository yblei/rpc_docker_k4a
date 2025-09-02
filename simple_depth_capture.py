#!/usr/bin/env python3
"""
Simple working depth capture for Mesa - following optimization guide
"""
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution, FPS
import time
import numpy as np
import os

def simple_depth_capture():
    print("Simple Mesa Depth Capture")
    print("=" * 25)
    
    # Use the most reliable configuration from the guide
    config = Config(
        color_resolution=ColorResolution.OFF,       # Depth-only for reliability
        depth_mode=DepthMode.NFOV_2X2BINNED,       # Lowest processing load
        camera_fps=FPS.FPS_5,                      # Conservative FPS
        synchronized_images_only=False,             # CRITICAL: No sync
        disable_streaming_indicator=True           # Reduce overhead
    )
    
    print("Configuration: Depth-only, 5 FPS, No sync")
    
    try:
        k4a = pyk4a.PyK4A(config=config)
        k4a.start()
        print("✓ Cameras started")
        
        # Stabilize
        print("Stabilizing (2 seconds)...")
        time.sleep(2)
        
        # Capture one frame and save it
        print("Capturing depth frame...")
        capture = k4a.get_capture()
        
        if capture.depth is not None:
            depth = capture.depth
            print(f"✓ Depth captured: {depth.shape}")
            print(f"  Range: {depth.min()}mm - {depth.max()}mm")
            
            # Save to current working directory (mounted volume)
            output_path = "/workspace/project/depth_image_simple.npy"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            np.save(output_path, depth)
            print(f"✓ Saved: {output_path}")
            
            # Also create a text file with info
            info_path = "/workspace/project/depth_info.txt"
            with open(info_path, 'w') as f:
                f.write(f"Depth Image Info\\n")
                f.write(f"================\\n")
                f.write(f"Shape: {depth.shape}\\n")
                f.write(f"Min depth: {depth.min()}mm\\n")
                f.write(f"Max depth: {depth.max()}mm\\n")
                f.write(f"Mean depth: {depth.mean():.1f}mm\\n")
                f.write(f"Configuration: Depth-only, NFOV_2X2BINNED, 5 FPS\\n")
            print(f"✓ Info saved: {info_path}")
            
        else:
            print("✗ No depth data received")
            return 1
        
        k4a.stop()
        print("✓ Cameras stopped")
        print("🎉 SUCCESS!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(simple_depth_capture())
