#!/usr/bin/env python3
"""
Example usage of RpcDockerK4a in user projects

This demonstrates how to use the rpc-docker-k4a package in external projects
after installing it with: pip install rpc-docker-k4a
"""

from rpc_docker_k4a import RpcDockerK4a
import time


def basic_usage_example():
    """Basic usage with context manager"""
    print("=== Basic Usage Example ===")
    
    # The combined class automatically starts server and provides client interface
    with RpcDockerK4a(verbose=True) as k4a:
        print(f"✅ Server started automatically on port {k4a.port}")
        
        # Connect to Azure Kinect device
        if k4a.connect_and_start():
            print("✅ Device connected and started")
            
            # Get device information
            k4a.get_device_status()
            
            # Capture some images
            print("\n📸 Capturing 3 images...")
            success = k4a.capture_and_save(count=3, filename_prefix="example")
            
            if success:
                print("✅ Images saved successfully")
            else:
                print("❌ Image capture failed")
            
            # Cleanup device
            k4a.cleanup()
        else:
            print("❌ Failed to connect to device (running in simulation mode)")
            print("📋 Device info:")
            k4a.get_device_status()
    
    print("✅ Server automatically stopped when context exited")


def advanced_usage_example():
    """Advanced usage with manual management"""
    print("\n=== Advanced Usage Example ===")
    
    # Manual instantiation with custom settings
    k4a = RpcDockerK4a(
        port=8005,
        verbose=True,
        auto_find_port=True  # Automatically find available port
    )
    
    try:
        print(f"✅ Server started on port {k4a.port}")
        
        # Check server status
        status = k4a.get_server_status()
        print(f"📊 Server PID: {status['pid']}, Running: {status['running']}")
        
        # Get detailed device and server info
        detailed_info = k4a.get_device_info_detailed()
        print(f"📋 Client URL: {detailed_info['client_url']}")
        
        # Demonstrate server restart capability
        print("\n🔄 Testing server restart...")
        k4a.restart_server()
        print("✅ Server restarted successfully")
        
    finally:
        # Manual cleanup (also happens automatically in destructor)
        del k4a
        print("✅ Server stopped")


def integration_example():
    """Example of integrating into a larger application"""
    print("\n=== Integration Example ===")
    
    class MyApplication:
        def __init__(self):
            # Initialize Azure Kinect as part of larger application
            self.kinect = RpcDockerK4a(verbose=False)  # Quiet mode
            self.is_running = False
        
        def start(self):
            """Start the application"""
            print("🚀 Starting application...")
            
            # Connect to device
            if self.kinect.connect_and_start():
                self.is_running = True
                print("✅ Application started with Azure Kinect")
                return True
            else:
                print("⚠️  Application started without Azure Kinect device")
                return False
        
        def capture_frame(self):
            """Capture a single frame"""
            if not self.is_running:
                print("❌ Application not running")
                return None
            
            try:
                # Use the XML-RPC interface directly for custom operations
                capture_result = self.kinect.server.get_capture(1000)
                if capture_result['success']:
                    print("📸 Frame captured")
                    return capture_result
                else:
                    print(f"❌ Capture failed: {capture_result['message']}")
                    return None
            except Exception as e:
                print(f"❌ Error capturing frame: {e}")
                return None
        
        def stop(self):
            """Stop the application"""
            if self.is_running:
                self.kinect.cleanup()
                self.is_running = False
            # Kinect server will stop automatically when object is destroyed
            print("🛑 Application stopped")
        
        def __enter__(self):
            self.start()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()
    
    # Use the application
    with MyApplication() as app:
        if app.is_running:
            # Capture a few frames
            for i in range(3):
                frame = app.capture_frame()
                if frame:
                    print(f"  Frame {i+1}: {frame['message']}")
                time.sleep(1)
        else:
            print("📋 Application running in simulation mode")


def main():
    """Run all examples"""
    print("🎯 RPC Docker K4A - Usage Examples")
    print("=" * 50)
    
    try:
        basic_usage_example()
        advanced_usage_example()
        integration_example()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error in examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main()
