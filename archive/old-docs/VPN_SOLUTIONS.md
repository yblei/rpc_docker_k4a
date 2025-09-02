# Azure Kinect VPN-Compatible Docker Solutions

## 🎯 Problem Solved
The Azure Kinect SDK fails to build in Docker when VPN is enabled due to DNS resolution issues. This repository provides VPN-compatible solutions.

## ✅ Available Solutions

### 1. Mesa Software Rendering (Recommended - Working)
- **Image**: `azure-kinect-mesa-vpn`
- **Base**: Ubuntu 18.04 + Mesa OpenGL software rendering
- **Status**: ✅ Fully working with depth capture
- **Performance**: Limited to depth-only at 5 FPS, supports async multi-stream
- **Build Command**: `./build-vpn.sh` (builds Mesa version)
- **Run Command**: `./run-kinect-vpn.sh`

### 2. Ubuntu 22.04 Source Build (In Development)
- **Image**: `azure-kinect-source-vpn`
- **Base**: Ubuntu 20.04 with NVIDIA OpenGL + source compilation
- **Status**: 🔄 Building from Microsoft's official repository
- **Performance**: Expected to be full performance with GPU acceleration
- **Build Command**: `docker build --network=host -t azure-kinect-source-vpn -f Dockerfile.k4a-source .`

## 🚀 Quick Start (VPN-Safe)

### Option 1: Use Pre-built Mesa Solution
```bash
# Run the VPN-compatible Mesa container
./run-kinect-vpn.sh

# Inside container - test depth capture
python3 -c "import pyk4a; print('pyk4a works!')"
k4aviewer  # Launch Kinect viewer
```

### Option 2: Build from Source (Modern approach)
```bash
# Build Ubuntu 22.04 version with source compilation
docker build --network=host -t azure-kinect-source-vpn -f Dockerfile.k4a-source .

# Run with NVIDIA support
docker run -it --rm --privileged \
    --runtime=nvidia \
    -e DISPLAY=${DISPLAY} \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev:/dev \
    azure-kinect-source-vpn
```

## 🔧 VPN Compatibility Features

### DNS Resolution Fixes
- Uses `--network=host` during Docker builds
- Docker Compose files include `dns: [8.8.8.8, 8.8.4.4]`
- Host networking bypasses VPN DNS issues

### Non-Interactive Builds
- `DEBIAN_FRONTEND=noninteractive` prevents hanging prompts
- `TZ=UTC` avoids timezone configuration dialogs
- `ACCEPT_EULA=Y` for Microsoft packages

## 📊 Performance Comparison

| Solution | Depth Capture | Color Capture | Multi-Stream | GPU Acceleration | VPN Safe |
|----------|---------------|---------------|--------------|------------------|----------|
| Mesa Software | ✅ 5 FPS | ✅ Limited | ⚠️ Async only | ❌ CPU only | ✅ Yes |
| Source Build | ✅ Expected | ✅ Expected | ✅ Expected | ✅ NVIDIA | ✅ Yes |
| Host System | ✅ 30 FPS | ✅ 30 FPS | ✅ Full sync | ✅ Hardware | N/A |

## 🐛 Known Limitations

### Mesa Solution (Current Working)
- **Performance**: Software rendering limits frame rates
- **Multi-stream**: Requires async mode, some timeout issues
- **GPU**: No hardware acceleration (CPU-only rendering)
- **Best Use**: Single depth stream, development, testing

### Source Build Solution (In Progress)  
- **Build Time**: Long compilation (30+ minutes)
- **Size**: Large image due to source compilation
- **Complexity**: More build dependencies
- **Best Use**: Production, high performance, multi-stream

## 📝 Technical Details

### Mesa OpenGL Configuration
```bash
LIBGL_ALWAYS_SOFTWARE=1      # Force software rendering
MESA_GL_VERSION_OVERRIDE=4.6 # OpenGL 4.6 support
MESA_GLSL_VERSION_OVERRIDE=460 # GLSL shader support
```

### NVIDIA Docker Configuration  
```yaml
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - NVIDIA_DRIVER_CAPABILITIES=all
  - __GLX_VENDOR_LIBRARY_NAME=nvidia
```

## 🎮 Usage Examples

### Depth Capture Test
```python
import pyk4a
from pyk4a import Config, PyK4A

# Initialize with depth-only config for best Mesa performance
config = Config(
    color_resolution=pyk4a.ColorResolution.OFF,
    depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
    synchronized_images_only=False,
    camera_fps=pyk4a.FPS.FPS_5
)

k4a = PyK4A(config=config)
k4a.start()

# Capture depth frame
capture = k4a.get_capture()
depth_image = capture.depth
print(f"Depth image shape: {depth_image.shape}")

k4a.stop()
```

### Multi-Stream Configuration
```python
# For Mesa - use async mode
config = Config(
    color_resolution=pyk4a.ColorResolution.RES_720P,
    depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
    synchronized_images_only=False,  # Important for Mesa
    camera_fps=pyk4a.FPS.FPS_5
)
```

## 🔍 Troubleshooting

### Build Issues with VPN
```bash
# If build fails with DNS errors
docker build --network=host -t image-name .

# Or use the provided VPN-safe scripts
./build-vpn.sh  # Builds both Mesa and source versions
```

### Runtime OpenGL Issues
```bash
# Check OpenGL in container
glxinfo | head -10

# Expected Mesa output:
# OpenGL vendor string: Mesa/X.org
# OpenGL renderer string: llvmpipe
# OpenGL version string: 4.6 (Compatibility Profile) Mesa
```

### USB Permission Issues
```bash
# On host system (run once)
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097a", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-k4a.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097b", MODE="0666", GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/99-k4a.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097c", MODE="0666", GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/99-k4a.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097d", MODE="0666", GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/99-k4a.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097e", MODE="0666", GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/99-k4a.rules

sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 🎯 Conclusion

The Mesa software rendering solution (`azure-kinect-mesa-vpn`) provides a **working VPN-compatible** Azure Kinect environment suitable for development and depth-only applications. For production use requiring full performance, the source build approach offers hardware acceleration at the cost of longer build times.

**Recommended for most users**: Start with the Mesa solution for immediate VPN compatibility, then migrate to source build for production deployments.
