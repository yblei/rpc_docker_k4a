#!/usr/bin/env python3

import sys
import time

def test_comprehensive_capture():
    """Test Azure Kinect with different configurations to find what works"""
    
    print("Testing Azure Kinect DK - Comprehensive test...")
    
    try:
        import pyk4a
        from pyk4a import Config, PyK4A
        print("[OK] Successfully imported pyk4a")
    except ImportError as e:
        print(f"[FAIL] Could not import pyk4a: {e}")
        return False
    
    # Test configurations in order of likelihood to work
    test_configs = [
        ("Color only", {
            'color_resolution': pyk4a.ColorResolution.RES_720P,
            'depth_mode': pyk4a.DepthMode.OFF,
            'camera_fps': pyk4a.FPS.FPS_30,
        }),
        ("Depth only - WFOV 2x2", {
            'color_resolution': pyk4a.ColorResolution.OFF,
            'depth_mode': pyk4a.DepthMode.WFOV_2X2BINNED,
            'camera_fps': pyk4a.FPS.FPS_30,
        }),
        ("Depth only - NFOV 2x2", {
            'color_resolution': pyk4a.ColorResolution.OFF,
            'depth_mode': pyk4a.DepthMode.NFOV_2X2BINNED,
            'camera_fps': pyk4a.FPS.FPS_30,
        }),
        ("Color + Depth WFOV 2x2", {
            'color_resolution': pyk4a.ColorResolution.RES_720P,
            'depth_mode': pyk4a.DepthMode.WFOV_2X2BINNED,
            'camera_fps': pyk4a.FPS.FPS_30,
            'synchronized_images_only': True,
        }),
    ]
    
    for config_name, config_params in test_configs:
        print(f"\n[TEST] {config_name}")
        print(f"[INFO] Config: {config_params}")
        
        try:
            config = Config(**config_params)
            k4a = PyK4A(config=config)
            
            print("[INFO] Starting camera...")
            k4a.start()
            
            print("[INFO] Camera started! Capturing frames...")
            
            success_count = 0
            for i in range(2):
                try:
                    capture = k4a.get_capture()
                    
                    if capture.color is not None:
                        print(f"  [SUCCESS] Color frame: {capture.color.shape}")
                        success_count += 1
                    
                    if capture.depth is not None:
                        depth = capture.depth
                        valid_pixels = (depth > 0).sum()
                        total_pixels = depth.size
                        print(f"  [SUCCESS] Depth frame: {depth.shape}, valid: {100*valid_pixels/total_pixels:.1f}%")
                        print(f"  [INFO] Depth range: {depth.min()}-{depth.max()}mm")
                        success_count += 1
                    
                    if capture.ir is not None:
                        print(f"  [SUCCESS] IR frame: {capture.ir.shape}")
                        success_count += 1
                        
                except Exception as e:
                    print(f"  [ERROR] Frame capture failed: {e}")
                
                time.sleep(0.3)
            
            k4a.stop()
            
            if success_count > 0:
                print(f"[SUCCESS] {config_name} - {success_count} successful captures!")
                if "depth" in config_name.lower() and success_count >= 2:
                    print("✅ DEPTH CAPTURE IS WORKING!")
                    return True
            else:
                print(f"[FAIL] {config_name} - No successful captures")
                
        except Exception as e:
            print(f"[FAIL] {config_name} failed: {e}")
            print(f"[DEBUG] Error type: {type(e).__name__}")
    
    return False

if __name__ == "__main__":
    success = test_comprehensive_capture()
    sys.exit(0 if success else 1)
