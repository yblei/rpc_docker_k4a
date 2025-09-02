#!/usr/bin/env python3
"""
Simple test using only k4aviewer (C++ tool) to test Azure Kinect basic functionality
This bypasses any Python pyk4a compilation issues
"""

import subprocess
import sys
import time

def test_k4aviewer():
    """Test if k4aviewer can detect the Azure Kinect device"""
    print("🔍 Testing Azure Kinect detection with k4aviewer...")
    
    try:
        # Try to run k4aviewer with --help to see if it works
        result = subprocess.run(['k4aviewer', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ k4aviewer is available")
            return True
        else:
            print(f"❌ k4aviewer failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ k4aviewer timed out")
        return False
    except FileNotFoundError:
        print("❌ k4aviewer not found")
        return False

def test_device_detection():
    """Test device detection using lsusb"""
    print("🔍 Checking USB device detection...")
    
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if '045e:097a' in result.stdout:
            print("✅ Azure Kinect USB device detected")
            return True
        else:
            print("❌ Azure Kinect USB device not found")
            print("Available USB devices:")
            for line in result.stdout.split('\n'):
                if 'Microsoft' in line or '045e' in line:
                    print(f"  📌 {line}")
            return False
    except Exception as e:
        print(f"❌ USB detection failed: {e}")
        return False

def main():
    print("🚀 Azure Kinect Docker Container Test")
    print("====================================")
    print()
    
    # Test 1: Device detection
    device_ok = test_device_detection()
    print()
    
    # Test 2: k4aviewer availability
    k4aviewer_ok = test_k4aviewer()
    print()
    
    # Summary
    if device_ok and k4aviewer_ok:
        print("🎉 SUCCESS: Container setup appears to be working!")
        print("   You can now try running: k4aviewer")
        return 0
    elif device_ok:
        print("⚠️  PARTIAL: Device detected but k4aviewer has issues")
        return 1
    else:
        print("❌ FAILED: Device not detected")
        return 2

if __name__ == "__main__":
    sys.exit(main())
