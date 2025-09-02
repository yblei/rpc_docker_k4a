#!/usr/bin/env python3
"""
Simple Azure Kinect test with error handling
"""
import sys

def test_basic_import():
    try:
        import pyk4a
        print("✓ pyk4a imported successfully")
        return True
    except Exception as e:
        print(f"✗ pyk4a import failed: {e}")
        return False

def test_device_count():
    try:
        import pyk4a
        count = pyk4a.PyK4A.device_get_installed_count()
        print(f"✓ Device count: {count}")
        return count > 0
    except Exception as e:
        print(f"✗ Device count failed: {e}")
        return False

def test_device_init_only():
    try:
        import pyk4a
        k4a = pyk4a.PyK4A()
        print("✓ Device initialization successful")
        return True
    except Exception as e:
        print(f"✗ Device init failed: {e}")
        return False

def test_opengl_context():
    print("OpenGL Environment:")
    import os
    print(f"  LIBGL_ALWAYS_SOFTWARE: {os.getenv('LIBGL_ALWAYS_SOFTWARE', 'not set')}")
    print(f"  MESA_GL_VERSION_OVERRIDE: {os.getenv('MESA_GL_VERSION_OVERRIDE', 'not set')}")
    print(f"  MESA_GLSL_VERSION_OVERRIDE: {os.getenv('MESA_GLSL_VERSION_OVERRIDE', 'not set')}")

if __name__ == "__main__":
    print("Azure Kinect Quick Test")
    print("=" * 30)
    
    test_opengl_context()
    print()
    
    if not test_basic_import():
        sys.exit(1)
    
    if not test_device_count():
        print("No devices found - this is expected if Kinect is not connected")
    
    test_device_init_only()
    
    print("\nBasic tests completed. Depth engine test would require device.start()")
