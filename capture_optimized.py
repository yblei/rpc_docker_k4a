#!/usr/bin/env python3
"""
Optimized depth capture for Mesa software rendering
"""
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution, FPS
import time
import os

def capture_with_optimized_settings():
    print("Optimized Azure Kinect Capture for Mesa")
    print("=" * 45)
    
    # Most reliable configuration for software rendering
    config = Config(
        color_resolution=ColorResolution.RES_1536P,  # Lower resolution
        depth_mode=DepthMode.NFOV_2X2BINNED,         # Lowest depth resolution  
        camera_fps=FPS.FPS_5,                        # Lowest FPS
        synchronized_images_only=False,               # Critical: No sync
        disable_streaming_indicator=True,            # Reduce LED overhead
    )
    
    print("Configuration:")
    print(f"  Color: {config.color_resolution}")
    print(f"  Depth: {config.depth_mode}") 
    print(f"  FPS: {config.camera_fps}")
    print(f"  Synchronized: {config.synchronized_images_only}")
    
    try:
        k4a = pyk4a.PyK4A(config=config)
        print("\n✓ Device initialized")
        
        print("Starting cameras...")
        k4a.start()
        print("✓ Cameras started")
        
        # Give cameras time to stabilize
        print("Stabilizing (3 seconds)...")
        time.sleep(3)
        
        # Capture frames with longer intervals
        successful_captures = 0
        for i in range(5):
            try:
                print(f"\nCapturing frame {i+1}/5...")
                
                # Get capture with no timeout (blocking)
                capture = k4a.get_capture()
                
                depth_shape = capture.depth.shape if capture.depth is not None else "None"
                color_shape = capture.color.shape if capture.color is not None else "None"
                
                print(f"  ✓ Depth: {depth_shape}")
                print(f"  ✓ Color: {color_shape}")
                
                # Save first successful capture
                if successful_captures == 0:
                    output_dir = "/workspace/project"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    if capture.depth is not None:
                        import numpy as np
                        np.save(f"{output_dir}/optimized_depth.npy", capture.depth)
                        print(f"  ✓ Saved depth to optimized_depth.npy")
                    
                    if capture.color is not None:
                        import numpy as np
                        np.save(f"{output_dir}/optimized_color.npy", capture.color)
                        print(f"  ✓ Saved color to optimized_color.npy")
                
                successful_captures += 1
                
                # Wait between captures to avoid overwhelming the system
                print("  Waiting 2 seconds...")
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Capture {i+1} failed: {e}")
        
        k4a.stop()
        print(f"\n✓ Cameras stopped")
        print(f"✓ Successfully captured {successful_captures}/5 frames")
        
        if successful_captures >= 3:
            print("🎉 SUCCESS: Multi-stream capture working!")
        else:
            print("⚠️  Partial success - consider depth-only mode")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def capture_depth_only_fast():
    """Fastest, most reliable depth-only capture"""
    print("\nDepth-Only Fast Capture")
    print("=" * 25)
    
    config = Config(
        color_resolution=ColorResolution.OFF,    # No color stream
        depth_mode=DepthMode.NFOV_2X2BINNED,    # Lowest resolution
        camera_fps=FPS.FPS_15,                  # Can go higher without color
        synchronized_images_only=False,
        disable_streaming_indicator=True,
    )
    
    try:
        k4a = pyk4a.PyK4A(config=config)
        k4a.start()
        print("✓ Depth-only cameras started at 15 FPS")
        
        time.sleep(1)  # Short stabilization
        
        for i in range(10):  # Capture more frames quickly
            capture = k4a.get_capture()
            if capture.depth is not None:
                print(f"  Frame {i+1}: {capture.depth.shape} - Min: {capture.depth.min()}mm, Max: {capture.depth.max()}mm")
            time.sleep(0.2)  # 5 FPS capture rate
        
        k4a.stop()
        print("✓ Depth-only capture successful!")
        
    except Exception as e:
        print(f"❌ Depth-only failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--depth-only":
        sys.exit(capture_depth_only_fast())
    else:
        result = capture_with_optimized_settings()
        if result != 0:
            print("\nTrying depth-only fallback...")
            result = capture_depth_only_fast()
        sys.exit(result)
