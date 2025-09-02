#!/usr/bin/env python3
"""
Azure Kinect depth capture example
Works with both Mesa and NVIDIA OpenGL versions
"""

import pyk4a
from pyk4a import Config, PyK4A
import cv2
import numpy as np

def main():
    print("Azure Kinect Depth Capture Example")
    print("===================================")
    
    try:
        # Initialize Azure Kinect
        k4a = PyK4A(Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
            synchronized_images_only=True,
        ))
        
        k4a.start()
        print("✅ Azure Kinect started successfully")
        
        # Capture frames
        for i in range(5):
            capture = k4a.get_capture()
            
            if capture.depth is not None:
                depth = capture.depth
                print(f"Frame {i+1}: Depth shape: {depth.shape}, range: {depth.min()}-{depth.max()}mm")
                
                # Save depth image as grayscale
                # Scale depth values to 0-255 for visualization
                depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                cv2.imwrite(f"depth_frame_{i+1}.png", depth_normalized)
                
            if capture.color is not None:
                color = capture.color
                print(f"Frame {i+1}: Color shape: {color.shape}")
                
                # Convert BGRA to BGR and save
                color_bgr = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(f"color_frame_{i+1}.jpg", color_bgr)
        
        k4a.stop()
        print("✅ Capture completed - check saved images")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Azure Kinect device is connected and powered on")

if __name__ == "__main__":
    main()
