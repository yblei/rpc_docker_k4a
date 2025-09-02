#!/usr/bin/env python3
"""
Capture and save Azure Kinect depth image from Docker container
"""
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution
import numpy as np
import time
import os

def save_depth_image():
    print("Azure Kinect Depth Image Capture")
    print("=" * 40)
    
    try:
        # Configure for depth capture
        config = Config(
            color_resolution=ColorResolution.RES_720P,
            depth_mode=DepthMode.NFOV_2X2BINNED,  # 320x288 depth resolution
            synchronized_images_only=True
        )
        
        print("Initializing Azure Kinect...")
        k4a = pyk4a.PyK4A(config=config)
        
        print("Starting cameras...")
        k4a.start()
        print("✓ Cameras started successfully!")
        
        # Wait a moment for cameras to stabilize
        print("Waiting for camera stabilization...")
        time.sleep(2)
        
        # Capture several frames to get a good one
        print("Capturing depth frame...")
        for attempt in range(5):
            capture = k4a.get_capture()
            if capture.depth is not None:
                depth_image = capture.depth
                print(f"✓ Depth frame captured: {depth_image.shape}")
                break
            time.sleep(0.1)
        else:
            raise Exception("Failed to capture depth frame after 5 attempts")
        
        # Get some statistics about the depth data
        valid_pixels = depth_image[depth_image > 0]
        if len(valid_pixels) > 0:
            depth_min = valid_pixels.min()
            depth_max = valid_pixels.max()
            depth_mean = valid_pixels.mean()
            print(f"  Depth range: {depth_min}mm - {depth_max}mm")
            print(f"  Mean depth: {depth_mean:.1f}mm")
            print(f"  Valid pixels: {len(valid_pixels)}/{depth_image.size} ({100*len(valid_pixels)/depth_image.size:.1f}%)")
        
        # Save as numpy array (.npy format) - preserves exact depth values
        output_dir = "/workspace/project"
        os.makedirs(output_dir, exist_ok=True)
        
        depth_npy_path = os.path.join(output_dir, "depth_image.npy")
        np.save(depth_npy_path, depth_image)
        print(f"✓ Depth data saved as: {depth_npy_path}")
        
        # Also save as 16-bit PNG for visualization
        # Scale depth to 16-bit range for PNG (0-65535)
        depth_normalized = np.clip(depth_image, 0, 8000)  # Clip to 8m max
        depth_16bit = (depth_normalized * 65535 / 8000).astype(np.uint16)
        
        # Try to save as PNG if opencv is available
        try:
            import cv2
            depth_png_path = os.path.join(output_dir, "depth_image.png")
            cv2.imwrite(depth_png_path, depth_16bit)
            print(f"✓ Depth PNG saved as: {depth_png_path}")
        except ImportError:
            print("  (OpenCV not available - PNG not saved)")
        
        # Save color image too if available
        if capture.color is not None:
            color_image = capture.color
            print(f"✓ Color frame captured: {color_image.shape}")
            
            color_npy_path = os.path.join(output_dir, "color_image.npy")
            np.save(color_npy_path, color_image)
            print(f"✓ Color data saved as: {color_npy_path}")
            
            # Save color as standard image
            try:
                import cv2
                # Convert BGRA to BGR for saving
                if color_image.shape[2] == 4:
                    color_bgr = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
                else:
                    color_bgr = color_image
                color_jpg_path = os.path.join(output_dir, "color_image.jpg")
                cv2.imwrite(color_jpg_path, color_bgr)
                print(f"✓ Color JPEG saved as: {color_jpg_path}")
            except ImportError:
                print("  (OpenCV not available - color image not saved)")
        
        # Create a simple text file with capture info
        info_path = os.path.join(output_dir, "capture_info.txt")
        with open(info_path, 'w') as f:
            f.write("Azure Kinect Depth Capture Info\n")
            f.write("=" * 35 + "\n\n")
            f.write(f"Depth Mode: {config.depth_mode}\n")
            f.write(f"Color Resolution: {config.color_resolution}\n")
            f.write(f"Depth Shape: {depth_image.shape}\n")
            if capture.color is not None:
                f.write(f"Color Shape: {capture.color.shape}\n")
            if len(valid_pixels) > 0:
                f.write(f"\nDepth Statistics:\n")
                f.write(f"  Range: {depth_min}mm - {depth_max}mm\n")
                f.write(f"  Mean: {depth_mean:.1f}mm\n")
                f.write(f"  Valid pixels: {len(valid_pixels)}/{depth_image.size} ({100*len(valid_pixels)/depth_image.size:.1f}%)\n")
        print(f"✓ Capture info saved as: {info_path}")
        
        print("\nStopping cameras...")
        k4a.stop()
        print("✓ Cameras stopped")
        
        print("\n🎉 SUCCESS! Depth image captured and saved!")
        print(f"Files saved in: {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(save_depth_image())
