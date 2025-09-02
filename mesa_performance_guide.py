#!/usr/bin/env python3
"""
Mesa Performance Optimization Tips for Azure Kinect Docker
"""

print("Azure Kinect Mesa Performance Optimization Guide")
print("=" * 55)

print("""
🎯 ROOT CAUSE:
Mesa software OpenGL rendering is CPU-intensive and much slower than GPU.
Multiple streams + synchronization + high FPS = timeout/performance issues.

🛠️ SOLUTIONS TO TRY:

1. DISABLE SYNCHRONIZATION (Most Important):
   synchronized_images_only=False
   
2. REDUCE COLOR RESOLUTION:
   ColorResolution.RES_1536P  # Instead of RES_720P
   
3. USE LOWEST FPS:
   FPS.FPS_5  # Start here, increase gradually
   
4. USE BINNED DEPTH MODE:
   DepthMode.NFOV_2X2BINNED  # Lowest processing load
   
5. DISABLE UNNECESSARY FEATURES:
   disable_streaming_indicator=True
   
6. CAPTURE WITH DELAYS:
   time.sleep(0.5)  # Between captures
   
7. CONSIDER DEPTH-ONLY FOR HIGH FPS:
   ColorResolution.OFF  # For > 5 FPS
   
8. MESA OPTIMIZATIONS:
   export MESA_GL_VERSION_OVERRIDE=4.6
   export MESA_GLSL_VERSION_OVERRIDE=460
   export GALLIUM_DRIVER=llvmpipe
   
9. SYSTEM OPTIMIZATIONS:
   - Increase Docker memory limit
   - Use --cpus for more CPU allocation
   - Reduce container overhead

📊 RECOMMENDED CONFIGURATIONS:

A) RELIABLE MULTI-STREAM:
   config = Config(
       color_resolution=ColorResolution.RES_1536P,
       depth_mode=DepthMode.NFOV_2X2BINNED,
       camera_fps=FPS.FPS_5,
       synchronized_images_only=False,  # KEY!
       disable_streaming_indicator=True
   )

B) FAST DEPTH-ONLY:
   config = Config(
       color_resolution=ColorResolution.OFF,
       depth_mode=DepthMode.NFOV_2X2BINNED,
       camera_fps=FPS.FPS_15,  # Can go higher
       synchronized_images_only=False
   )

C) MAXIMUM PERFORMANCE DEPTH-ONLY:
   config = Config(
       color_resolution=ColorResolution.OFF,
       depth_mode=DepthMode.NFOV_2X2BINNED,
       camera_fps=FPS.FPS_30,
       synchronized_images_only=False
   )

⚡ IMMEDIATE FIXES TO TRY:

1. Set synchronized_images_only=False
2. Use time.sleep(0.5) between get_capture() calls  
3. Start with FPS_5 and increase gradually
4. Use lower color resolution (1536P instead of 720P)

The key insight: Mesa software rendering can't keep up with hardware 
timing expectations, so async mode + slower capture rates work better.
""")

# Example working configuration
print("\n" + "="*55)
print("EXAMPLE WORKING CODE:")
print("="*55)

code_example = '''
import pyk4a
from pyk4a import Config, DepthMode, ColorResolution, FPS
import time

# Most reliable configuration for Mesa
config = Config(
    color_resolution=ColorResolution.RES_1536P,  # Lower than 720P
    depth_mode=DepthMode.NFOV_2X2BINNED,         # Lowest processing
    camera_fps=FPS.FPS_5,                        # Conservative FPS
    synchronized_images_only=False,               # CRITICAL: No sync
    disable_streaming_indicator=True             # Reduce overhead
)

k4a = pyk4a.PyK4A(config=config)
k4a.start()

# Stabilize
time.sleep(2)

# Capture with delays
for i in range(5):
    capture = k4a.get_capture()
    print(f"Frame {i}: Depth={capture.depth.shape if capture.depth else None}")
    time.sleep(0.5)  # Key: Don't capture too fast

k4a.stop()
'''

print(code_example)
