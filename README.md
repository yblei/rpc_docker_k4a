# Azure Kinect Docker Solutions

This repository provides two working Docker solutions for Azure Kinect SDK on Ubuntu 22.04:

## 🎯 Two Working Solutions

### 1. Mesa Software Rendering (Universal)
- **Use case**: Works on any system without GPU setup requirements
- **Pros**: Universal compatibility, no NVIDIA drivers needed
- **Cons**: Software rendering only
- **Files**: `Dockerfile.mesa`, `deploy-mesa-vpn.sh`

### 2. NVIDIA OpenGL Hardware Acceleration 
- **Use case**: High-performance applications requiring GPU acceleration
- **Pros**: Full hardware acceleration, better performance
- **Cons**: Requires NVIDIA GPU and Docker runtime setup
- **Files**: `Dockerfile.k4a-prebuilt`, `deploy-prebuilt-vpn.sh`

## 🚀 Quick Start

### Option 1: Mesa Version (Universal)
```bash
# Build
./build-mesa-vpn.sh

# Run
./deploy-mesa-vpn.sh
```

### Option 2: NVIDIA OpenGL Version (Hardware Accelerated)
```bash
# Build  
./build-prebuilt-vpn.sh

# Run
./deploy-prebuilt-vpn.sh
```

## ✅ Verified Features

Both solutions provide:
- ✅ Azure Kinect SDK 1.4
- ✅ Depth image capture (576x640)
- ✅ Color image capture (720x1280)
- ✅ Python pyk4a integration
- ✅ k4a-tools (k4aviewer, etc.)
- ✅ VPN compatibility
- ✅ USB device access

## 📋 Requirements

### Mesa Version
- Docker
- USB access to Azure Kinect device
- X11 forwarding for GUI applications

### NVIDIA Version  
- Docker with NVIDIA runtime
- NVIDIA GPU with drivers
- USB access to Azure Kinect device
- X11 forwarding for GUI applications

## 🔧 Device Setup

Copy udev rules for device access:
```bash
sudo cp 99-k4a.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

## 📝 Usage Examples

### Python Depth Capture
```python
import pyk4a
from pyk4a import Config, PyK4A

k4a = PyK4A(Config(
    color_resolution=pyk4a.ColorResolution.RES_720P,
    depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
    synchronized_images_only=True,
))
k4a.start()
capture = k4a.get_capture()
print(f"Depth: {capture.depth.shape}")
print(f"Color: {capture.color.shape}")
```

### K4A Viewer
```bash
# Inside container
k4aviewer
```

## 🏗️ Architecture

Both solutions use:
- Ubuntu 22.04 base
- Microsoft prebuilt packages (no source compilation)
- Automatic EULA acceptance
- VPN-compatible networking

## 🆘 Troubleshooting

### Common Issues
- **EULA errors**: Handled automatically in both solutions
- **USB permissions**: Use provided udev rules  
- **X11 display**: Ensure `xhost +` is run on host
- **NVIDIA runtime**: Install nvidia-docker2 for hardware acceleration

### Choosing the Right Solution
- Use **Mesa version** for development, testing, or systems without NVIDIA GPU
- Use **NVIDIA version** for production applications requiring high performance

## �� References
- [Azure Kinect SDK Documentation](https://docs.microsoft.com/en-us/azure/kinect-dk/)
- [Installation Guide Reference](https://atlane.de/install-azure-kinect-sdk-1-4-on-ubuntu-22-04/)
