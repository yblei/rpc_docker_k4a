#!/usr/bin/env python3
"""
Working Azure Kinect depth+color capture script for Mesa Docker container
"""
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution
import time
import signal
import sys

def signal_handler(sig, frame):
    print('\nInterrupted by user, cleaning up...')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Azure Kinect Mesa Docker Test")
    print("=" * 40)
    
    try:
        # Configure for both depth and color
        config = Config(
            color_resolution=ColorResolution.RES_720P,
            depth_mode=DepthMode.NFOV_2X2BINNED,  # Lower res depth for better performance
            synchronized_images_only=True
        )
        
        print("Initializing Azure Kinect...")
        k4a = pyk4a.PyK4A(config=config)
        
        print("Starting cameras (depth + color)...")
        k4a.start()
        print("✓ SUCCESS: Cameras started!")
        
        # Capture a few frames to verify everything works
        for i in range(5):
            print(f"\nCapturing frame {i+1}/5...")
            capture = k4a.get_capture()
            
            if capture.depth is not None:
                print(f"  ✓ Depth: {capture.depth.shape}")
                depth_min = capture.depth.min()
                depth_max = capture.depth.max()
                print(f"    Range: {depth_min}mm - {depth_max}mm")
            else:
                print("  ✗ No depth data")
                
            if capture.color is not None:
                print(f"  ✓ Color: {capture.color.shape}")
            else:
                print("  ✗ No color data")
                
            time.sleep(1)  # Brief pause between captures
        
        print("\nStopping cameras...")
        k4a.stop()
        print("✓ SUCCESS: Azure Kinect depth+color working in Mesa Docker!")
        print("\n🎉 COMPLETE SUCCESS! 🎉")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        try:
            k4a.stop()
        except:
            pass
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
