#!/usr/bin/env python3
"""
Performance-optimized Azure Kinect configuration for Docker Mesa
"""
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution, ImageFormat, FPS
import time

def test_performance_configs():
    print("Azure Kinect Performance Testing")
    print("=" * 40)
    
    # Test different configurations from most to least demanding
    configs = [
        {
            "name": "Depth Only - 5 FPS (Working baseline)",
            "config": Config(
                color_resolution=ColorResolution.OFF,
                depth_mode=DepthMode.NFOV_2X2BINNED,
                camera_fps=FPS.FPS_5,
                synchronized_images_only=False,
            )
        },
        {
            "name": "Depth Only - 15 FPS",
            "config": Config(
                color_resolution=ColorResolution.OFF,
                depth_mode=DepthMode.NFOV_2X2BINNED,
                camera_fps=FPS.FPS_15,
                synchronized_images_only=False,
            )
        },
        {
            "name": "Depth + Color - 5 FPS (Async)",
            "config": Config(
                color_resolution=ColorResolution.RES_720P,
                depth_mode=DepthMode.NFOV_2X2BINNED,
                camera_fps=FPS.FPS_5,
                synchronized_images_only=False,  # Key: Allow async
            )
        },
        {
            "name": "Depth + Color - 5 FPS (Sync)",
            "config": Config(
                color_resolution=ColorResolution.RES_720P,
                depth_mode=DepthMode.NFOV_2X2BINNED,
                camera_fps=FPS.FPS_5,
                synchronized_images_only=True,  # This often causes timeouts
            )
        },
        {
            "name": "Lower Color Resolution - 5 FPS",
            "config": Config(
                color_resolution=ColorResolution.RES_1536P,  # Lower than 720P
                depth_mode=DepthMode.NFOV_2X2BINNED,
                camera_fps=FPS.FPS_5,
                synchronized_images_only=False,
            )
        }
    ]
    
    for test_config in configs:
        print(f"\n{'='*50}")
        print(f"Testing: {test_config['name']}")
        print(f"{'='*50}")
        
        try:
            k4a = pyk4a.PyK4A(config=test_config['config'])
            print("✓ Device initialized")
            
            start_time = time.time()
            k4a.start()
            startup_time = time.time() - start_time
            print(f"✓ Cameras started in {startup_time:.2f}s")
            
            # Try to capture 3 frames
            successful_captures = 0
            for i in range(3):
                try:
                    capture_start = time.time()
                    capture = k4a.get_capture(timeout_in_ms=2000)  # 2 second timeout
                    capture_time = time.time() - capture_start
                    
                    depth_info = f"{capture.depth.shape}" if capture.depth is not None else "None"
                    color_info = f"{capture.color.shape}" if capture.color is not None else "None"
                    
                    print(f"  Frame {i+1}: Depth={depth_info}, Color={color_info} ({capture_time:.2f}s)")
                    successful_captures += 1
                    
                except Exception as e:
                    print(f"  Frame {i+1}: TIMEOUT/ERROR - {e}")
            
            k4a.stop()
            print(f"✓ Result: {successful_captures}/3 frames successful")
            
            if successful_captures == 3:
                print("🎉 CONFIGURATION WORKS!")
            elif successful_captures > 0:
                print("⚠️  PARTIAL SUCCESS - Some timeouts")
            else:
                print("❌ FAILED - All frames timed out")
                
        except Exception as e:
            print(f"❌ FAILED to start: {e}")
        
        print("\nWaiting 3 seconds before next test...")
        time.sleep(3)

def get_optimized_config():
    """Return the most optimal configuration for Mesa software rendering"""
    return Config(
        color_resolution=ColorResolution.RES_1536P,  # Lower resolution than 720P
        depth_mode=DepthMode.NFOV_2X2BINNED,         # Lowest depth resolution
        camera_fps=FPS.FPS_5,                        # Lowest FPS
        synchronized_images_only=False,               # Allow async capture
        depth_delay_off_color_usec=0,                # No delay
        wired_sync_mode=0,                           # Standalone mode
        subordinate_delay_off_master_usec=0,         # No sync delay
        disable_streaming_indicator=True,            # Reduce overhead
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_performance_configs()
    else:
        print("Optimized Azure Kinect Configuration")
        print("Use --test flag to run performance tests")
        config = get_optimized_config()
        print(f"Recommended config: {config}")
