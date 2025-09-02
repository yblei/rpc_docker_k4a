#!/usr/bin/env python3
"""
Azure Kinect RPC Client Example
Demonstrates how to use the Azure Kinect RPC server remotely

Usage:
    python3 kinect_rpc_client.py [--host HOST] [--port PORT]
"""

import argparse
import xmlrpc.client
import base64
import numpy as np
import cv2
import time

class AzureKinectRPCClient:
    def __init__(self, host='localhost', port=8000):
        self.server_url = f"http://{host}:{port}"
        self.server = xmlrpc.client.ServerProxy(self.server_url, allow_none=True)
    
    def connect_and_start(self):
        """Connect to device and start capture"""
        print("Connecting to Azure Kinect...")
        
        # Connect with default configuration
        config = {
            'color_resolution': '720P',
            'depth_mode': 'NFOV_UNBINNED',
            'camera_fps': 30,
            'synchronized_images_only': True
        }
        
        result = self.server.device_connect(config)
        print(f"Connect: {result['message']}")
        if not result['success']:
            return False
        
        # Start device
        result = self.server.device_start()
        print(f"Start: {result['message']}")
        return result['success']
    
    def capture_and_display(self):
        """Capture and display images"""
        print("\nCapturing frames... (Press 'q' to quit)")
        
        cv2.namedWindow('Azure Kinect - Color', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Azure Kinect - Depth', cv2.WINDOW_AUTOSIZE)
        
        try:
            while True:
                # Get capture
                capture_result = self.server.get_capture(1000)  # 1 second timeout
                if not capture_result['success']:
                    print(f"Capture failed: {capture_result['message']}")
                    time.sleep(0.1)
                    continue
                
                # Get color image
                color_result = self.server.get_color_image('BGR', 85)
                if color_result['success']:
                    # Decode base64 image
                    image_data = base64.b64decode(color_result['image_data'])
                    image_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                    
                    # Add info overlay
                    cv2.putText(image_np, f"Shape: {color_result['shape']}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(image_np, f"FPS: {1.0/0.033:.1f}", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Azure Kinect - Color', image_np)
                
                # Get depth image (colormap version for visualization)
                depth_result = self.server.get_depth_image('COLORMAP', 0, 4000)
                if depth_result['success']:
                    # Decode base64 image
                    image_data = base64.b64decode(depth_result['image_data'])
                    depth_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                    
                    # Add info overlay
                    depth_range = depth_result['depth_range']
                    cv2.putText(depth_np, f"Shape: {depth_result['shape'][:2]}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(depth_np, f"Range: {depth_range[0]}-{depth_range[1]}mm", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Azure Kinect - Depth', depth_np)
                
                # Check for exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        cv2.destroyAllWindows()
    
    def save_images(self, count=5):
        """Capture and save images to disk"""
        print(f"\nSaving {count} image pairs...")
        
        for i in range(count):
            # Get capture
            capture_result = self.server.get_capture(2000)
            if not capture_result['success']:
                print(f"Capture {i+1} failed: {capture_result['message']}")
                continue
            
            # Save color image
            color_result = self.server.get_color_image('JPEG', 95)
            if color_result['success']:
                image_data = base64.b64decode(color_result['image_data'])
                with open(f'color_frame_{i+1:03d}.jpg', 'wb') as f:
                    f.write(image_data)
            
            # Save depth image (normalized grayscale)
            depth_result = self.server.get_depth_image('NORMALIZED', 0, 4000)
            if depth_result['success']:
                image_data = base64.b64decode(depth_result['image_data'])
                with open(f'depth_frame_{i+1:03d}.png', 'wb') as f:
                    f.write(image_data)
            
            print(f"Saved frame {i+1}/{count}")
            time.sleep(0.5)
        
        print(f"Saved {count} image pairs to current directory")
    
    def get_device_status(self):
        """Get and display device information"""
        info = self.server.get_device_info()
        print("\n=== Device Information ===")
        print(f"Connected: {info['connected']}")
        print(f"Started: {info['started']}")
        print(f"Serial: {info.get('serial', 'N/A')}")
        print(f"Simulation Mode: {info.get('simulation_mode', False)}")
        
        if 'available_modes' in info:
            modes = info['available_modes']
            print(f"Available color resolutions: {', '.join(modes['color_resolutions'])}")
            print(f"Available depth modes: {', '.join(modes['depth_modes'])}")
            print(f"Available frame rates: {', '.join(map(str, modes['frame_rates']))}")
    
    def cleanup(self):
        """Stop and disconnect from device"""
        print("\nCleaning up...")
        try:
            self.server.device_stop()
            self.server.device_disconnect()
            print("Device disconnected")
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Azure Kinect RPC Client')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--mode', choices=['display', 'save', 'info'], default='display',
                       help='Operation mode (default: display)')
    parser.add_argument('--count', type=int, default=5, help='Number of images to save (default: 5)')
    
    args = parser.parse_args()
    
    client = AzureKinectRPCClient(args.host, args.port)
    
    try:
        # Test server connection
        try:
            methods = client.server.system.listMethods()
            print(f"Connected to Azure Kinect RPC Server at {client.server_url}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            print(f"Make sure the server is running at {client.server_url}")
            return
        
        if args.mode == 'info':
            # Just show device info
            client.get_device_status()
            return
        
        # Connect and start device
        if not client.connect_and_start():
            print("Failed to initialize device")
            return
        
        # Show device status
        client.get_device_status()
        
        if args.mode == 'display':
            # Live display mode
            client.capture_and_display()
        elif args.mode == 'save':
            # Save images mode
            client.save_images(args.count)
        
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client.cleanup()

if __name__ == "__main__":
    main()
