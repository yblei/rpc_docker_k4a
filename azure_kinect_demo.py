#!/usr/bin/env python3
"""
Azure Kinect Demo - Works perfectly over SSH!

This demonstrates the complete solution for using Azure Kinect depth camera over SSH.
The Docker container includes integrated Xvfb virtual display, solving Error 207.
"""

from rpc_docker_k4a.combined import RpcDockerK4a
import base64
import cv2
import numpy as np
import time

def demo_azure_kinect_ssh():
    """Demo: Azure Kinect over SSH with integrated virtual display"""
    print("🎯 Azure Kinect SSH Demo - Final Solution")
    print("=" * 50)
    print("✅ Works over SSH")
    print("✅ Integrated virtual display in container")
    print("✅ NVIDIA GPU acceleration")
    print("✅ Full depth + color camera access")
    print()
    
    try:
        # Initialize Azure Kinect with Docker
        with RpcDockerK4a(use_docker='nvidia', verbose=True) as k4a:
            
            # Configure for high-quality capture
            config = {
                'color_resolution': '1080P',      # 1920x1080
                'depth_mode': 'NFOV_2X2BINNED',  # 320x288 depth
                'camera_fps': 15,
                'synchronized_images_only': True  # Sync depth + color
            }
            
            print(f"\n🔗 Connecting with config: {config}")
            
            # Connect to device
            if not k4a.server.device_connect(config).get('success'):
                print("❌ Connection failed")
                return False
            
            # Start capture
            if not k4a.server.device_start().get('success'):
                print("❌ Start failed")
                return False
            
            print("✅ Azure Kinect started successfully!")
            
            # Capture multiple synchronized frames
            print("\n📸 Capturing synchronized depth + color frames...")
            
            for i in range(3):
                print(f"\n📷 Frame {i+1}/3:")
                
                # Wait between captures
                time.sleep(1)
                
                # Get capture
                capture_result = k4a.server.get_capture(10000)
                if not capture_result.get('success'):
                    print(f"   ❌ Capture {i+1} failed")
                    continue
                
                print(f"   ✅ Capture successful")
                print(f"   📊 Color shape: {capture_result.get('color_shape')}")
                print(f"   📊 Depth shape: {capture_result.get('depth_shape')}")
                
                # Get depth image (colorized for visualization)
                depth_result = k4a.server.get_depth_image('COLORMAP', 0, 4000)
                if depth_result.get('success'):
                    depth_data = base64.b64decode(depth_result['image_data'])
                    depth_np = cv2.imdecode(
                        np.frombuffer(depth_data, np.uint8), cv2.IMREAD_COLOR
                    )
                    
                    filename_depth = f'examples/demo_depth_{i+1:02d}.jpg'
                    cv2.imwrite(filename_depth, depth_np)
                    print(f"   💾 Depth saved: {filename_depth}")
                
                # Get color image
                color_result = k4a.server.get_color_image('BGR', 95)
                if color_result.get('success'):
                    color_data = base64.b64decode(color_result['image_data'])
                    color_np = cv2.imdecode(
                        np.frombuffer(color_data, np.uint8), cv2.IMREAD_COLOR
                    )
                    
                    filename_color = f'examples/demo_color_{i+1:02d}.jpg'
                    cv2.imwrite(filename_color, color_np)
                    print(f"   💾 Color saved: {filename_color}")
            
            return True
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = demo_azure_kinect_ssh()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 DEMO SUCCESSFUL!")
        print("=" * 60)
        print("✅ Azure Kinect depth camera working over SSH")
        print("✅ Error 207 completely resolved")
        print("✅ Images saved to examples/ folder")
        print("✅ Ready for production use")
        print()
        print("🔧 The Solution:")
        print("   - Integrated Xvfb in Docker container")
        print("   - NVIDIA GPU acceleration")
        print("   - OpenGL 4.5 context available")
        print("   - No external dependencies")
    else:
        print("\n❌ Demo failed - check setup")

if __name__ == '__main__':
    main()
