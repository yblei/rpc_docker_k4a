#!/usr/bin/env python3
"""
Comprehensive Azure Kinect depth test for Docker container
"""
import sys
import os

def test_imports():
    print("=== Testing Python imports ===")
    try:
        import pyk4a
        print("✓ pyk4a imported successfully")
        print(f"  pyk4a version: {pyk4a.__version__ if hasattr(pyk4a, '__version__') else 'unknown'}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import pyk4a: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error importing pyk4a: {e}")
        return False

def test_device_detection():
    print("\n=== Testing device detection ===")
    try:
        import pyk4a
        
        # Check for device count
        device_count = pyk4a.PyK4A.device_get_installed_count()
        print(f"  Found {device_count} Azure Kinect device(s)")
        
        if device_count == 0:
            print("✗ No Azure Kinect devices detected")
            return False
            
        print("✓ Azure Kinect device detected")
        return True
        
    except Exception as e:
        print(f"✗ Device detection failed: {e}")
        return False

def test_device_initialization():
    print("\n=== Testing device initialization ===")
    try:
        import pyk4a
        from pyk4a import Config
        
        # Try to initialize device
        k4a = pyk4a.PyK4A(Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
            synchronized_images_only=True,
        ))
        
        print("✓ Device initialization successful")
        
        # Try to start the device (this tests the depth engine)
        print("  Starting device (testing depth engine)...")
        k4a.start()
        print("✓ Device started successfully (depth engine working!)")
        
        # Try to get a frame
        print("  Attempting to capture frame...")
        capture = k4a.get_capture()
        
        if capture.depth is not None:
            depth_shape = capture.depth.shape
            print(f"✓ Depth frame captured: {depth_shape}")
        else:
            print("✗ No depth data in capture")
            
        if capture.color is not None:
            color_shape = capture.color.shape
            print(f"✓ Color frame captured: {color_shape}")
        else:
            print("✗ No color data in capture")
            
        # Clean up
        k4a.stop()
        print("✓ Device stopped cleanly")
        return True
        
    except Exception as e:
        print(f"✗ Device initialization failed: {e}")
        return False

def main():
    print("Azure Kinect Docker Container Test")
    print("=" * 50)
    
    # Test environment
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    tests = [
        test_imports,
        test_device_detection, 
        test_device_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Unexpected error in {test.__name__}: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Depth engine is working in Docker!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
